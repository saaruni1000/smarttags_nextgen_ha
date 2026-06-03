import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import SmartTagsAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class SmartTagCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, cookie_string, csrf_token):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
            always_update=False
        )
        self.api = SmartTagsAPI(async_get_clientsession(hass), cookie_string, csrf_token)
        self.last_known_timestamp = "20260603193003" 

    async def _async_update_data(self):
        """Fetch and normalize data from the custom endpoint."""
        device_id = "759751163" 
        
        operations = await self.api.get_device_locations(device_id, self.last_known_timestamp)
        if not operations:
            raise UpdateFailed("No operational tracking data returned from Samsung")

        normalized_data = {
            "device_id": device_id,
            "latitude": None,
            "longitude": None,
            "battery": None,
            "location_type": None
        }

        for oprn in operations:
            if oprn.get("oprnType") == "LOCATION":
                normalized_data["latitude"] = float(oprn.get("latitude"))
                normalized_data["longitude"] = float(oprn.get("longitude"))
                normalized_data["location_type"] = oprn.get("locationType")
                
                if "extra" in oprn and "gpsUtcDt" in oprn["extra"]:
                    self.last_known_timestamp = oprn["extra"]["gpsUtcDt"]
                
            elif oprn.get("oprnType") == "CHECK_CONNECTION":
                normalized_data["battery"] = oprn.get("battery")

        return normalized_data