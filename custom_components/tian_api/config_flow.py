"""Config flow for Tian API integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN, NAME, CONF_API_KEY

class TianConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tian API."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            
            # 简单验证API密钥长度
            if len(api_key) == 32:
                return self.async_create_entry(
                    title=NAME,
                    data={CONF_API_KEY: api_key}
                )
            else:
                errors["base"] = "invalid_api_key_format"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": NAME
            }
        )