from __future__ import annotations

import asyncio
from typing import Dict

import plotly.express as px
import streamlit as st

# Bootstrap PYTHONPATH so imports resolve when running from the repo root
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.orchestrator.llm.client import chat_complete
from services.orchestrator.vector.client import vector_client
from shared.models import TicketType

st.set_page_config(page_title="ServiceNow Analyst", layout="wide", page_icon="🎫")

_loop = asyncio.new_event_loop()


def _run(coro):
    return _loop.run_until_complete(coro)


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.title("ServiceNow Analyst")
page = st.sidebar.radio(
    "Navigate",
    ["Semantic Search", "Similar Tickets", "Trend Analysis"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Page: Semantic Search
# ──────────────────────────────────────────────────────────────────────────────
if page == "Semantic Search":
    st.title("Semantic Ticket Search")
    st.caption("Search across all historical tickets using natural language.")

    query = st.text_input("Describe the issue or request you're looking for:")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_types = st.multiselect(
            "Ticket types",
            options=[t.value for t in TicketType],
            default=[t.value for t in TicketType],
        )
    with col2:
        top_k = st.slider("Results", min_value=3, max_value=20, value=8)
    with col3:
        summarize = st.checkbox("LLM summary", value=True)

    if st.button("Search", type="primary") and query:
        with st.spinner("Searching…"):
            types = [TicketType(t) for t in selected_types]
            results = _run(vector_client.search_similar(query, ticket_types=types, limit=top_k))

        if not results:
            st.info("No results found. Try a different query or broaden the ticket types.")
        else:
            if summarize:
                with st.spinner("Generating summary…"):
                    excerpts = "\n\n".join(
                        f"[{r.ticket_number}] {r.excerpt}" for r in results[:5]
                    )
                    summary_prompt = (
                        f"The analyst searched for: '{query}'\n\n"
                        f"Top matching tickets:\n{excerpts}\n\n"
                        "Summarize the key patterns, common themes, and relevant resolutions "
                        "from these tickets in 3-4 sentences."
                    )
                    msg = _run(chat_complete(
                        messages=[
                            {"role": "system", "content": "You are an IT analyst assistant. Be concise and actionable."},
                            {"role": "user", "content": summary_prompt},
                        ],
                        temperature=0.3,
                        max_tokens=300,
                    ))
                    st.info(msg.content or "")

            for r in results:
                with st.expander(f"[{r.ticket_type.value.upper()}] {r.ticket_number} — score: {r.score:.3f}"):
                    st.write(r.excerpt)
                    if r.metadata:
                        st.json({k: v for k, v in r.metadata.items() if v})

# ──────────────────────────────────────────────────────────────────────────────
# Page: Similar Tickets
# ──────────────────────────────────────────────────────────────────────────────
elif page == "Similar Tickets":
    st.title("Find Similar Tickets")
    st.caption("Paste a ticket description to find the closest historical matches before creating a new one.")

    description = st.text_area("Ticket description:", height=150)
    limit = st.slider("Number of results", 3, 15, 5)

    if st.button("Find Similar", type="primary") and description:
        with st.spinner("Finding similar tickets…"):
            results = _run(vector_client.search_similar(description, limit=limit))

        if not results:
            st.info("No similar tickets found.")
        else:
            st.success(f"Found {len(results)} similar ticket(s):")
            for r in results:
                col_a, col_b = st.columns([1, 5])
                with col_a:
                    st.metric("Similarity", f"{r.score:.1%}")
                with col_b:
                    st.markdown(f"**[{r.ticket_type.value.upper()}] {r.ticket_number}**")
                    st.write(r.excerpt)
                st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Page: Trend Analysis
# ──────────────────────────────────────────────────────────────────────────────
elif page == "Trend Analysis":
    st.title("Trend Analysis")
    st.caption("Explore volume and patterns across historical tickets.")

    col1, col2 = st.columns(2)
    with col1:
        selected_type = st.selectbox("Ticket type", [t.value for t in TicketType])
    with col2:
        trend_query = st.text_input("Focus area (optional):", placeholder="e.g. VPN, printer, password reset")

    if st.button("Analyze", type="primary"):
        ticket_type = TicketType(selected_type)
        with st.spinner("Fetching data…"):
            # Pull a sample of recent tickets from Qdrant using a broad query
            sample_query = trend_query or f"common {selected_type} issues"
            results = _run(vector_client.search_similar(sample_query, ticket_types=[ticket_type], limit=50))

        if not results:
            st.warning("Not enough data for trend analysis. Run the ingestion pipeline first.")
        else:
            # Category distribution from metadata
            categories: Dict[str, int] = {}
            for r in results:
                cat = r.metadata.get("category") or "Uncategorized"
                categories[cat] = categories.get(cat, 0) + 1

            if len(categories) > 1:
                fig = px.bar(
                    x=list(categories.keys()),
                    y=list(categories.values()),
                    labels={"x": "Category", "y": "Count"},
                    title=f"Top Categories — {selected_type.title()}",
                )
                st.plotly_chart(fig, use_container_width=True)

            # LLM narrative
            with st.spinner("Generating narrative…"):
                excerpts = "\n".join(
                    f"- [{r.ticket_number}] {r.excerpt[:150]}" for r in results[:20]
                )
                focus = f" focused on '{trend_query}'" if trend_query else ""
                narrative_prompt = (
                    f"Analyze these {selected_type}{focus} tickets and identify: "
                    "1) the most common issues, 2) recurring patterns or root causes, "
                    "3) any actionable recommendations to reduce future tickets.\n\n"
                    f"Tickets:\n{excerpts}"
                )
                msg = _run(chat_complete(
                    messages=[
                        {"role": "system", "content": "You are a senior IT analyst. Be specific and actionable. Use bullet points."},
                        {"role": "user", "content": narrative_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=500,
                ))
                st.markdown("### Analysis")
                st.markdown(msg.content or "")
