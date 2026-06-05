import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class SmartTagsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartThings Find NextGen."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(title="Samsung SmartTags", data=user_input)

        data_schema = vol.Schema({
            vol.Required("jsession_id"): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                "url": "https://smartthingsfind.samsung.com/"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Tell Home Assistant we support a configuration options menu."""
        return SmartTagsOptionsFlowHandler(config_entry)


class SmartTagsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the Options/Configure menu."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Use an underscore to avoid colliding with HA 2024's protected properties
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options step."""
        if user_input is not None:
            # Update the core data with the new JSESSIONID
            self.hass.config_entries.async_update_entry(
                self._config_entry, data={**self._config_entry.data, "jsession_id": user_input["jsession_id"]}
            )
            # Reload the integration so the API class grabs the fresh token
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        # Pre-fill the box with their current token so they can verify or replace it
        current_id = self._config_entry.data.get("jsession_id", "")
        
        options_schema = vol.Schema({
            vol.Required("jsession_id", default=current_id): str
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "url": "https://smartthingsfind.samsung.com/"
            }
        )