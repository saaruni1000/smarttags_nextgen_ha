from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the SmartTag device tracker platform for multiple tags."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    # Loop through the dictionary keys (device IDs) the coordinator built
    for device_id, tag_data in coordinator.data.items():
        name = tag_data.get("name", "SmartTag")
        entities.append(SmartTagTracker(coordinator, device_id, name))
        
    async_add_entities(entities)

class SmartTagTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a specific Samsung SmartTag on the HA Map."""

    def __init__(self, coordinator, device_id, name):
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"smarttag_{device_id}"
        self._attr_name = name

    # Helper property to quickly grab this specific tag's data block
    @property
    def tag_data(self):
        return self.coordinator.data.get(self.device_id, {})

    @property
    def latitude(self):
        return self.tag_data.get("latitude")

    @property
    def longitude(self):
        return self.tag_data.get("longitude")

    @property
    def source_type(self):
        return "gps"

    @property
    def battery_level(self):
        battery_map = {"HIGH": 100, "MEDIUM": 50, "LOW": 10}
        current_battery = self.tag_data.get("battery", "UNKNOWN")
        return battery_map.get(current_battery)

    @property
    def icon(self):
        return "mdi:tag-location"
        
    @property
    def extra_state_attributes(self):
        return {
            "location_type": self.tag_data.get("location_type")
        }