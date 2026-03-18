import json
from pathlib import Path
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

mcp = FastMCP("WeatherNotes")

# ─────────────────────────────────────────
# NOTES STORAGE  (persisted to a JSON file)
# ─────────────────────────────────────────
NOTES_FILE = Path(__file__).parent / "notes.json"


def load_notes() -> dict:
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text())
    return {}


def save_notes(notes: dict):
    NOTES_FILE.write_text(json.dumps(notes, indent=2))


# ─────────────────────────────────────────
# WEATHER HELPERS  (Open-Meteo — free, no API key)
# ─────────────────────────────────────────
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 99: "Thunderstorm with hail",
}


def get_coordinates(city: str) -> tuple[float, float, str]:
    """Get lat/lon for a city using the free Open-Meteo geocoding API."""
    resp = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("results"):
        raise ValueError(f"City '{city}' not found.")
    r = data["results"][0]
    return r["latitude"], r["longitude"], r["name"]


def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo."""
    resp = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
            "wind_speed_unit": "kmh",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["current"]


# ─────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for any city in the world."""
    try:
        lat, lon, resolved_name = get_coordinates(city)
        weather = fetch_weather(lat, lon)
        code = weather.get("weathercode", 0)
        condition = WMO_CODES.get(code, "Unknown")
        return (
            f"Weather in {resolved_name}:\n"
            f"  Condition   : {condition}\n"
            f"  Temperature : {weather['temperature_2m']} C\n"
            f"  Humidity    : {weather['relative_humidity_2m']}%\n"
            f"  Wind Speed  : {weather['wind_speed_10m']} km/h"
        )
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error fetching weather: {e}"


@mcp.tool()
def add_note(title: str, body: str) -> str:
    """Add a new note. Returns the new note ID."""
    notes = load_notes()
    new_id = str(max((int(k) for k in notes), default=0) + 1)
    notes[new_id] = {"title": title, "body": body}
    save_notes(notes)
    return f"Note created with ID: {new_id}"


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Delete a note by its ID."""
    notes = load_notes()
    if note_id not in notes:
        return f"Note '{note_id}' not found."
    del notes[note_id]
    save_notes(notes)
    return f"Note '{note_id}' deleted."


@mcp.tool()
def update_note(note_id: str, title: str, body: str) -> str:
    """Update the title and body of an existing note."""
    notes = load_notes()
    if note_id not in notes:
        return f"Note '{note_id}' not found."
    notes[note_id] = {"title": title, "body": body}
    save_notes(notes)
    return f"Note '{note_id}' updated."


# ─────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────

@mcp.resource("notes://all")
def resource_all_notes() -> str:
    """List all saved notes (ID + title)."""
    notes = load_notes()
    if not notes:
        return "No notes found."
    return "\n".join(f"[{nid}] {n['title']}" for nid, n in notes.items())


@mcp.resource("notes://{note_id}")
def resource_get_note(note_id: str) -> str:
    """Get the full content of a note by ID."""
    notes = load_notes()
    note = notes.get(note_id)
    if not note:
        return f"Note '{note_id}' not found."
    return f"Title: {note['title']}\n\nBody: {note['body']}"


@mcp.resource("weather://{city}")
def resource_weather(city: str) -> str:
    """Get current weather for a city as a resource."""
    return get_weather(city)


# ─────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────

@mcp.prompt()
def daily_briefing(city: str) -> list[PromptMessage]:
    """Generate a morning briefing with weather and a summary of all notes."""
    weather_info = get_weather(city)
    notes = load_notes()
    notes_text = "\n".join(
        f"[{nid}] {n['title']}: {n['body']}" for nid, n in notes.items()
    ) or "No notes yet."

    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=(
                    f"Good morning! Here is my daily briefing:\n\n"
                    f"--- WEATHER ({city}) ---\n{weather_info}\n\n"
                    f"--- MY NOTES ---\n{notes_text}\n\n"
                    f"Please give me a friendly morning summary with key things to remember."
                ),
            ),
        )
    ]


@mcp.prompt()
def summarize_notes() -> list[PromptMessage]:
    """Summarize all notes concisely."""
    notes = load_notes()
    notes_text = "\n".join(
        f"[{nid}] {n['title']}: {n['body']}" for nid, n in notes.items()
    ) or "No notes yet."
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Here are my notes:\n\n{notes_text}\n\nSummarize them in 2-3 sentences.",
            ),
        )
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
