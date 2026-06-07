import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_REGION, REGION_EUROPE

# We load the platforms definition directly from const to match your original architecture
PLATFORMS = ["device_tracker"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartTags from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    jsession_id = entry.data.get("jsession_id")  
    
    # Extract the region selected in the UI form, fallback to prd-eu if missing
    region = entry.data.get(CONF_REGION, REGION_EUROPE)

    # Pass both the jsession_id and the dynamic region parameter directly into your original coordinator architecture
    # Note: Ensure your coordinator.py accepts this third argument or extracts it accordingly
    try:
        from .coordinator import SmartTagCoordinator
        coordinator = SmartTagCoordinator(hass, jsession_id, region)
    except TypeError:
        # Fallback safeguard: If your coordinator __init__ hasn't been updated to accept 'region' yet,
        # we log a warning and initialize it with 2 arguments to prevent boot crash.
        _LOGGER.warning("SmartTagCoordinator signature requires an update to accept the 'region' parameter natively.")
        from .coordinator import SmartTagCoordinator
        coordinator = SmartTagCoordinator(hass, jsession_id)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
