"""Config flow for SmartThings Find NextGen integration."""
import logging
from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# Fixed: Added REGION_ASIA_2 to the source import parameters mapping
from .const import DOMAIN, CONF_JSESSION_ID, CONF_REGION, REGION_EUROPE, REGION_US_GENERAL, REGION_ASIA, REGION_ASIA_2
from .api import SmartTagsAPI

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input by attempting a login with the selected region."""
    session = async_get_clientsession(hass)
    
    # Instantiate the API orchestrator with the chosen region from the dropdown form
    api = SmartTagsAPI(session, data[CONF_JSESSION_ID], data[CONF_REGION])
    
    # Pre-flight validation check executing a dynamic CSRF exchange
    success = await api.refresh_csrf_token()
    if not success:
        raise config_entries.exceptions.InvalidAuth
        
    devices = await api.get_devices()
    if devices is None:
        raise config_entries.exceptions.CannotConnect
        
    return {"title": "SmartThings Find Account"}

class SmartTagsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartThings Find NextGen."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> Any:
        """Handle the initial step creating the interactive UI configurations."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except config_entries.exceptions.InvalidAuth:
                errors["base"] = "invalid_auth"
            except config_entries.exceptions.CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception occurred during validation")
                errors["base"] = "unknown"

        # Explicit key-value mapping dict linking internal region values to friendly readable UI names
        region_options = {
            REGION_EUROPE: "Europe (prd-eu)",
            REGION_US_GENERAL: "General / US (prd-us)",
            REGION_ASIA: "Asia / Pacific (prd-ap)",
            REGION_ASIA_2: "Asia / Pacific 2 (prd-ap2)"
        }

        data_schema = vol.Schema({
            vol.Required(CONF_JSESSION_ID): str,
            vol.Required(CONF_REGION, default=REGION_EUROPE): vol.In(region_options)
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
