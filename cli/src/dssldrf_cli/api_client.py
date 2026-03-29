# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any
import httpx


class ApiClient:
    def __init__(self, api_url: str, token: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.token = token.strip()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(timeout=20.0, verify=False) as client:
            response = client.get(
                f"{self.api_url}{path}",
                headers=self._headers(),
                params=params,
            )
        self._raise_on_error(response)
        return response.json()

    def post(self, path: str, payload: dict[str, Any]) -> Any:
        with httpx.Client(timeout=20.0, verify=False) as client:
            response = client.post(
                f"{self.api_url}{path}",
                headers=self._headers(),
                json=payload,
            )
        self._raise_on_error(response)
        return response.json()

    def delete(self, path: str) -> Any:
        with httpx.Client(timeout=20.0, verify=False) as client:
            response = client.delete(
                f"{self.api_url}{path}",
                headers=self._headers(),
            )
        self._raise_on_error(response)
        if not response.text:
            return {"status": "success"}
        return response.json()

    def list_rules(self, zone: str) -> list[dict[str, Any]]:
        # Directly perform the request so we can treat 404 ("no rules") as an empty list
        with httpx.Client(timeout=20.0, verify=False) as client:
            response = client.get(
                f"{self.api_url}/rules/{zone}",
                headers=self._headers(),
            )

        if response.status_code == 404:
            # The API returns 404 when a zone has no rules; treat this as an empty list
            return []

        self._raise_on_error(response)
        result = response.json()
        if isinstance(result, list):
            return result
        return []

    def create_rule(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = self.post("/rules", payload)
        if isinstance(result, dict):
            return result
        raise RuntimeError("Unexpected response for create_rule")

    def delete_rule(self, zone: str, rule_id: str) -> dict[str, Any]:
        result = self.delete(f"/rules/{zone}/{rule_id}")
        if isinstance(result, dict):
            return result
        return {"status": "success"}

    def add_rule_component(self, zone: str, rule_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self.post(f"/rules/{zone}/{rule_id}/components", payload)
        if isinstance(result, dict):
            return result
        raise RuntimeError("Unexpected response for add_rule_component")

    def delete_rule_component(self, zone: str, rule_id: str, component_id: str) -> dict[str, Any]:
        result = self.delete(f"/rules/{zone}/{rule_id}/components/{component_id}")
        if isinstance(result, dict):
            return result
        return {"status": "success"}

    @staticmethod
    def _raise_on_error(response: httpx.Response) -> None:
        if response.status_code < 400:
            return

        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"API {response.status_code}: {detail}")
