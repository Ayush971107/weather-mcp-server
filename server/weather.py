from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        

def format_alert(feature: dict) -> dict:
    """Format an alert feature into a JSON/dict object."""
    props = feature["properties"]
    return {
        "Event": props.get("event", "Unknown"),
        "Area": props.get("areaDesc", "Unknown"),
        "Severity": props.get("severity", "Unknown"),
        "Description": props.get("description", "No description available"),
        "Instructions": props.get("instruction", "No specific instructions provided"),
    }

@mcp.tool()
async def get_alerts(state: str) -> list[dict]:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g., CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return []  # or {"error": "Unable to fetch alerts or no alerts found."}

    if not data["features"]:
        return []

    alerts = [format_alert(feature) for feature in data["features"]]
    return alerts


