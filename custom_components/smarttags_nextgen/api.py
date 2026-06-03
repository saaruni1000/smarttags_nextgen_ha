import aiohttp
import logging
from typing import Dict, Any, Optional, List

_LOGGER = logging.getLogger(__name__)

class SmartTagsAPI:
    def __init__(self, session: aiohttp.ClientSession, cookie_string: str, csrf_token: str):
        self.session = session
        self.csrf_token = csrf_token
        
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,he;q=0.8,ja;q=0.7",
            "content-type": "application/json",
            "Cookie": cookie_string,
            "origin": "https://smartthingsfind.samsung.com",
            "priority": "u=1, i",
            "referer": "https://smartthingsfind.samsung.com/",
            "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }

    async def get_devices(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch the list of all registered devices."""
        url = f"https://smartthingsfind.samsung.com/device/getDeviceList.do?_csrf={self.csrf_token}"
        
        try:
            async with self.session.post(url, headers=self.headers, json={}) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to fetch device list. Status: %s", resp.status)
                    return None
                    
                data = await resp.json()
                device_list = data.get("deviceList", [])
                # LOGGING: Total count of connected Samsung hardware
                _LOGGER.info("SmartThings Find: Found %s total devices in Samsung account", len(device_list))
                return device_list
                
        except Exception as e:
            _LOGGER.error("Network error fetching device list: %s", e)
            return None

    async def get_device_locations(self, device_id: str, latest_time: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch tracking matrices from Samsung."""
        url = f"https://smartthingsfind.samsung.com/dm/getTagLocation.do?_csrf={self.csrf_token}"
        
        payload = {
            "dvceId": device_id,
            "latestTime": latest_time
        }

        try:
            async with self.session.post(url, headers=self.headers, json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("API tracking failed for device %s with status: %s", device_id, resp.status)
                    return None
                    
                data = await resp.json()
                return data.get("operation", [])
                
        except Exception as e:
            _LOGGER.error("Network execution error inside custom integration: %s", e)
            return None