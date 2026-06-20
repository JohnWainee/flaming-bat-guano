from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from shared.config import settings
from shared.models import TicketCreated, TicketType

_SNOW_TABLE_MAP: Dict[TicketType, str] = {
    TicketType.INCIDENT: "incident",
    TicketType.REQUEST: "sc_request",
    TicketType.CHANGE: "change_request",
    TicketType.PROBLEM: "problem",
}

_SNOW_NUMBER_FIELD: Dict[str, str] = {
    "incident": "number",
    "sc_request": "number",
    "change_request": "number",
    "problem": "number",
}


class ServiceNowClient:
    def __init__(self) -> None:
        self._base = settings.snow_instance_url.rstrip("/")
        self._timeout = httpx.Timeout(settings.snow_api_timeout_seconds)
        self._oauth_token: Optional[str] = None

    def _auth_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if settings.snow_auth_method == "oauth" and self._oauth_token:
            headers["Authorization"] = f"Bearer {self._oauth_token}"
        return headers

    def _make_client(self) -> httpx.AsyncClient:
        kwargs: Dict[str, Any] = {"timeout": self._timeout, "headers": self._auth_headers()}
        if settings.snow_auth_method == "basic":
            kwargs["auth"] = (settings.snow_username or "", settings.snow_password or "")
        return httpx.AsyncClient(**kwargs)

    async def _refresh_oauth_token(self) -> None:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base}/oauth_token.do",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.snow_client_id,
                    "client_secret": settings.snow_client_secret,
                },
            )
            resp.raise_for_status()
            self._oauth_token = resp.json()["access_token"]

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        retry_on_401: bool = True,
    ) -> Any:
        async with self._make_client() as client:
            resp = await client.request(method, f"{self._base}{path}", params=params, json=json)
            if resp.status_code == 401 and retry_on_401 and settings.snow_auth_method == "oauth":
                await self._refresh_oauth_token()
                return await self._request(method, path, params=params, json=json, retry_on_401=False)
            resp.raise_for_status()
            return resp.json().get("result", resp.json())

    async def create_ticket(self, ticket_type: TicketType, fields: Dict[str, Any]) -> TicketCreated:
        table = _SNOW_TABLE_MAP[ticket_type]
        result = await self._request("POST", f"/api/now/table/{table}", json=fields)
        number = result.get("number", result.get("sys_id", "UNKNOWN"))
        sys_id = result.get("sys_id", "")
        return TicketCreated(
            ticket_number=number,
            sys_id=sys_id,
            ticket_type=ticket_type,
            snow_url=f"{self._base}/nav_to.do?uri=/{table}.do?sys_id={sys_id}",
        )

    async def get_ticket(self, table: str, sys_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if fields:
            params["sysparm_fields"] = ",".join(fields)
        return await self._request("GET", f"/api/now/table/{table}/{sys_id}", params=params)

    async def update_ticket(self, table: str, sys_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PATCH", f"/api/now/table/{table}/{sys_id}", json=fields)

    async def query_records(
        self,
        table: str,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "sysparm_query": query,
            "sysparm_limit": limit,
            "sysparm_offset": offset,
        }
        if fields:
            params["sysparm_fields"] = ",".join(fields)
        result = await self._request("GET", f"/api/now/table/{table}", params=params)
        if isinstance(result, list):
            return result
        return []

    async def iter_all_records(
        self,
        table: str,
        query: str,
        fields: Optional[List[str]] = None,
        page_size: int = 1000,
        rate_limit_delay: float = 0.5,
    ) -> AsyncIterator[Dict[str, Any]]:
        offset = 0
        while True:
            batch = await self.query_records(table, query, fields=fields, limit=page_size, offset=offset)
            for record in batch:
                yield record
            if len(batch) < page_size:
                break
            offset += page_size
            await asyncio.sleep(rate_limit_delay)


snow_client = ServiceNowClient()
