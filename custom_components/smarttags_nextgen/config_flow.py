import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SmartTagsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartThings Find NextGen."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user submits the session identifier."""
        if user_input is not None:
            return self.async_create_entry(title="Samsung SmartTags", data=user_input)

        # Prompt for the exact structural token needed
        data_schema = vol.Schema({
            vol.Required("jsession_id", description={"suggested_value": "3AA5...fmm-prd"}): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema
        )