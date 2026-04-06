import requests
import os
import logging
import config

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_alert(event: dict):
    """Send a Telegram message for high-value events."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return  # Silently skip if not configured
    
    if not config.ENABLE_TELEGRAM_ALERTS:
        return

    deadline = event.get("nomination_deadline", "")
    name = event.get("event_name", "Unknown")
    sector = event.get("sector", "")
    date = event.get("date", "TBD")
    location = event.get("location", "India")
    url = event.get("source_url", "")
    confidence = event.get("confidence", 0)
    
    emoji = "🏆" if event.get("event_type") == "awards" else "🎤"
    
    message = f"""{emoji} *New High-Value Discovery!*

📌 *{name}*
🏷️ Sector: {sector}
📅 Date: {date}
📍 Location: {location}
⏰ Deadline: {deadline if deadline else 'Not specified'}
✅ Confidence: {confidence}%
🔗 {url}"""
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
        if response.status_code != 200:
            logger.error(f"Telegram alert failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Telegram alert exception: {e}")


def should_alert(event: dict) -> bool:
    """Return True if this event deserves a Telegram alert."""
    return (
        event.get("confidence", 0) >= 80 and
        event.get("event_type") == "awards" and
        bool(event.get("nomination_deadline"))
    )
