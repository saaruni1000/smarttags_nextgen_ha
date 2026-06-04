# smarttags_nextgen_ha
Viewing smart tags locations on Home Assistant

This project currently only allows to see the locations of the smart tags and not control them in any way. I don't currently plan to try and add these things.

I only have 1 smart tag so I haven't tested it with more than 1, it should work as I dynamically get the list but it might be broken on certain conditions. If you find bugs, feel free to open an issue.

## Installation

### Method 1: HACS (Recommended)

Since this integration is not currently in the default HACS store, you can easily add it as a Custom Repository:

1. Open **HACS** in your Home Assistant dashboard.
2. Click the **three dots** in the top right corner and select **Custom repositories**.
3. Paste the URL of this GitHub repository into the **Repository** box.
4. For **Category**, select **Integration**.
5. Click **Add**.
6. Find the **Samsung SmartTags NextGen** integration in the list and click **Download**.
7. Restart Home Assistant.

---

### Method 2: Manual Installation

If you prefer not to use HACS, you can install the integration files directly onto your server:

1. Download the latest release source code (or clone this repository).
2. Using an SSH client, Samba, or the File Editor add-on, locate your Home Assistant `config/` directory.
3. Look for a folder named `custom_components`. If it does not exist, create it.
4. Copy the `smarttags_nextgen_ha` folder from this repository into your `custom_components/` directory.

## Setup Instructions

1. Go to the Integrations page.
2. Search "SmartThings Find NextGen".
3. Visit https://smartthingsfind.samsung.com/ and log in with your Samsung account.
4. Open Developer Tools in your browser.
5. Copy the JSESSIONID value. Note to copy the one from smartthingsfind.samsung.com (you might have another from another domain).
6. Enter your JSESSIONID into Home Assistant.
7. Enjoy :)

## Debuging

To enable debugging, you need to set the log level in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.smartthings_find: debug
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! Feel free to open issues or submit pull requests to help improve this integration.

## Support

For support, please create an issue on the GitHub repository.

## Roadmap

- Maybe more comfortable login

## Disclaimer

This is a third-party integration and is not affiliated with or endorsed by Samsung or SmartThings.