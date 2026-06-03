import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import SmartTagsAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class SmartTagCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, cookie_string):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
            always_update=False
        )
        # Note: No longer passing a hardcoded csrf_token here
        self.api = SmartTagsAPI(async_get_clientsession(hass), cookie_string)
        self.last_known_timestamps = {}

    async def _async_update_data(self):
        """Automatically refresh the CSRF shield, fetch device list, and synchronize states."""
        # 1. Dynamically capture the fresh token first
        token_success = await self.api.refresh_csrf_token()
        if not token_success:
            raise UpdateFailed("Failed to dynamically acquire operational CSRF token from Samsung session.")

        # 2. Proceed with standard multi-device tracking loop
        devices = await self.api.get_devices()
        if devices is None:
            raise UpdateFailed("Failed to communicate with Samsung Device List endpoint.")

        tags = [d for d in devices if d.get("deviceType") == "TAG"]
        _LOGGER.info("SmartThings Find: Identified %s tracking tags to process", len(tags))
        
        old_data = self.data if self.data else {}
        normalized_data = {}

        for tag in tags:
            device_id = tag.get("dvceID")
            name = tag.get("nickName") or tag.get("modelName", "SmartTag")
            
            if device_id not in self.last_known_timestamps:
                self.last_known_timestamps[device_id] = "20260603193003"

            operations = await self.api.get_device_locations(device_id, self.last_known_timestamps[device_id])
            old_tag_data = old_data.get(device_id, {})

            tag_data = {
                "device_id": device_id,
                "name": name,
                "latitude": old_tag_data.get("latitude"),
                "longitude": old_tag_data.get("longitude"),
                "battery": old_tag_data.get("battery"),
                "location_type": old_tag_data.get("location_type")
            }

            if operations:
                for oprn in operations:
                    if oprn.get("oprnType") == "LOCATION":
                        tag_data["latitude"] = float(oprn.get("latitude"))
                        tag_data["longitude"] = float(oprn.get("longitude"))
                        tag_data["location_type"] = oprn.get("locationType")
                        
                        if "extra" in oprn and "gpsUtcDt" in oprn["extra"]:
                            self.last_known_timestamps[device_id] = oprn["extra"]["gpsUtcDt"]
                            
                    elif oprn.get("oprnType") == "CHECK_CONNECTION":
                        tag_data["battery"] = oprn.get("battery")
            
            _LOGGER.info(
                "SmartThings Find Tracker Status Update -> Name: %s | ID: %s | Lat: %s | Lon: %s | Battery: %s",
                tag_data["name"],
                tag_data["device_id"],
                tag_data["latitude"],
                tag_data["longitude"],
                tag_data["battery"]
            )
                        
            normalized_data[device_id] = tag_data

        return normalized_data