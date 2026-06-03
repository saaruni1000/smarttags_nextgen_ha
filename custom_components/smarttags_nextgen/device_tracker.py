from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the SmartTag device tracker platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartTagTracker(coordinator)])

class SmartTagTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a Samsung SmartTag on the HA Map."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"smarttag_{self.coordinator.data.get('device_id')}"
        self._attr_name = "My SmartTag"

    @property
    def latitude(self):
        """Return latitude value from the coordinator."""
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        """Return longitude value from the coordinator."""
        return self.coordinator.data.get("longitude")

    @property
    def source_type(self):
        """Identify state values as explicit GPS coordinates."""
        return "gps"

    @property
    def battery_level(self):
        """Translate text status matrices into a readable percentage."""
        battery_map = {"HIGH": 100, "MEDIUM": 50, "LOW": 10}
        current_battery = self.coordinator.data.get("battery", "UNKNOWN")
        return battery_map.get(current_battery)

    @property
    def icon(self):
        """Set fallback rendering design icon."""
        return "mdi:tag-location"
        
    @property
    def extra_state_attributes(self):
        """Pass additional variables into entity states."""
        return {
            "location_type": self.coordinator.data.get("location_type")
        }