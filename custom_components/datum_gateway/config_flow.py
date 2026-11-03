"""Config flow for one DATUM Gateway."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_URL, DOMAIN


class DatumGatewayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for the JSON API base URL and check the public stats endpoint."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = str(user_input["url"]).strip().rstrip("/")
            name = str(user_input.get("name") or "").strip()
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                errors["base"] = "invalid_url"
            else:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                try:
                    session = async_get_clientsession(self.hass)
                    async with asyncio.timeout(15):
                        async with session.get(
                            f"{url}/v1/decentralized_client_stats"
                        ) as resp:
                            resp.raise_for_status()
                            body = await resp.json(content_type=None)
                    if not isinstance(body, dict) or "ready" not in body:
                        errors["base"] = "cannot_connect"
                    else:
                        data = {"url": url}
                        if name:
                            data["name"] = name
                        return self.async_create_entry(
                            title=name or "DATUM Gateway",
                            data=data,
                        )
                except Exception:
                    errors["base"] = "cannot_connect"
            user_input = {"url": url, "name": name}
        entered = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("url", default=entered.get("url", DEFAULT_URL)): str,
                    vol.Optional("name", default=entered.get("name", "")): str,
                }
            ),
            errors=errors,
        )
