import aiohttp
import logging
import json
from typing import Dict, Any, Optional, List

_LOGGER = logging.getLogger(__name__)

class SmartTagsAPI:
    def __init__(self, session: aiohttp.ClientSession, jsession_id: str):
        self.session = session
        self.jsession_id = jsession_id
        self.csrf_token: Optional[str] = None
    
        # Construct the Cookie header dynamically using only the JSESSIONID
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,he;q=0.8,ja;q=0.7",
            "Cookie": f"JSESSIONID={self.jsession_id}",
            "origin": "https://smartthingsfind.samsung.com",
            "priority": "u=1, i",
            "referer": "https://smartthingsfind.samsung.com/",
            "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "x-fmm-origin": "prd-eu",  # format 1
            "x-fmm-orgin": "prd-eu"    # format 2
        }

    async def set_last_select(self, device_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch the absolute latest baseline state and timestamp for a newly initialized device."""
        if not self.csrf_token:
            return None

        url = f"https://smartthingsfind.samsung.com/device/setLastSelect.do?_csrf={self.csrf_token}"
        headers = {**self.headers, "content-type": "application/json"}
        payload = {"dvceId": device_id}

        try:
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("API setLastSelect failed for device %s with status: %s", device_id, resp.status)
                    return None
                    
                data = await resp.json()
                return data.get("operation", [])
        except Exception as e:
            _LOGGER.error("Network error during setLastSelect baseline fetch: %s", e)
            return None

    async def refresh_csrf_token(self) -> bool:  
        """Fetch a fresh CSRF token from the chkLogin endpoint."""
        url = "https://smartthingsfind.samsung.com/chkLogin.do"
        try:
            async with self.session.get(url, headers=self.headers) as resp:
                csrf = resp.headers.get("_csrf") or resp.headers.get("X-CSRF-TOKEN")
                
                if csrf:
                    self.csrf_token = csrf
                    _LOGGER.info("SmartThings Find: Successfully refreshed CSRF token dynamically")
                    return True
                
                _LOGGER.error(f"Response received: headers: {resp.headers}")
                
                # check for contant
                text_data = await resp.text()
                if text_data and len(text_data) > 4:
                    try:
                        data = json.loads(text_data)
                        _LOGGER.error(f"Response received: body: {data}")
                    except Exception:
                        _LOGGER.error(f"Response body is not a valid JSON string: {text_data}")
                else:
                    _LOGGER.error(f"Response body is empty or too short (Length: {len(text_data) if text_data else 0})")
                
                _LOGGER.error("SmartThings Find: chkLogin responded but '_csrf' header was missing. Session might be invalid.")
                return False
        except Exception as e:
            _LOGGER.error("Network error attempting to refresh CSRF token: %s", e)
            return False

    async def get_devices(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch the list of all registered devices."""
        if not self.csrf_token:
            _LOGGER.error("Cannot fetch devices: CSRF token is missing or uninitialized")
            return None

        url = f"https://smartthingsfind.samsung.com/device/getDeviceList.do?_csrf={self.csrf_token}"
        headers = {**self.headers, "content-type": "application/json"}
        
        try:
            async with self.session.post(url, headers=headers, json={}) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to fetch device list. Status: %s", resp.status)
                    return None
                    
                data = await resp.json()
                device_list = data.get("deviceList", [])
                _LOGGER.info("SmartThings Find: Found %s total devices in Samsung account", len(device_list))
                return device_list
        except Exception as e:
            _LOGGER.error("Network error fetching device list: %s", e)
            return None

    async def get_device_locations(self, device_id: str, latest_time: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch tracking matrices from Samsung."""
        if not self.csrf_token:
            return None

        url = f"https://smartthingsfind.samsung.com/dm/getTagLocation.do?_csrf={self.csrf_token}"
        headers = {**self.headers, "content-type": "application/json"}
        payload = {"dvceId": device_id, "latestTime": latest_time}

        try:
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("API tracking failed for device %s with status: %s", device_id, resp.status)
                    return None
                    
                data = await resp.json()
                return data.get("operation", [])
        except Exception as e:
            _LOGGER.error("Network execution error inside custom integration: %s", e)
            return None
