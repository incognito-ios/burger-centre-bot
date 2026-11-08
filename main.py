
import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

CATEGORIES = {
    "people": {
        "name": "👤 People Search",
        "links": [
            ("TruePeopleSearch", "https://www.truepeoplesearch.com/"),
            ("FastPeopleSearch", "https://www.fastpeoplesearch.com/"),
            ("Whitepages", "https://www.whitepages.com/"),
            ("That'sThem", "https://thatsthem.com/"),
            ("PeopleFinders", "https://www.peoplefinders.com/")
        ]
    },
    "phone": {
        "name": "📞 Phone & Email",
        "links": [
            ("Phone Validator", "https://www.numverify.com/"),
            ("Phone Search", "https://www.google.com/search?q=phone+number+lookup"),
            ("Have I Been Pwned", "https://haveibeenpwned.com/"),
            ("Hunter", "https://hunter.io/")
        ]
    },
    "search": {
        "name": "🔎 Search Engines",
        "links": [
            ("Google", "https://www.google.com/"),
            ("Bing", "https://www.bing.com/"),
            ("DuckDuckGo", "https://duckduckgo.com/"),
            ("Brave Search", "https://search.brave.com/"),
            ("Yandex", "https://yandex.com/")
        ]
    },
    "social": {
        "name": "📱 Social Media",
        "links": [
            ("Social Searcher", "https://www.social-searcher.com/"),
            ("Namechk", "https://namechk.com/"),
            ("WhatsMyName", "https://whatsmyname.app/")
        ]
    },
    "images": {
        "name": "🖼 Image Search",
        "links": [
            ("Google Lens", "https://lens.google.com/"),
            ("TinEye", "https://tineye.com/"),
            ("Bing Visual Search", "https://www.bing.com/visualsearch"),
            ("Yandex Images", "https://yandex.com/images/")
        ]
    },
    "maps": {
        "name": "📍 Maps & Locations",
        "links": [
            ("Google Maps", "https://maps.google.com/"),
            ("OpenStreetMap", "https://www.openstreetmap.org/"),
            ("Google Earth", "https://earth.google.com/"),
            ("What3Words", "https://what3words.com/")
        ]
    },
    "business": {
        "name": "🏢 Business Directories",
        "links": [
            ("BBB", "https://www.bbb.org/"),
            ("OpenCorporates", "https://opencorporates.com/"),
            ("Google Business", "https://www.google.com/business/"),
            ("Yellow Pages", "https://www.yellowpages.com/")
        ]
    },
    "records": {
        "name": "📂 Public Records",
        "links": [
            ("PACER", "https://pacer.uscourts.gov/"),
            ("USA.gov", "https://www.usa.gov/"),
            ("SEC EDGAR", "https://www.sec.gov/edgar"),
            ("National Archives", "https://www.archives.gov/")
        ]
    },
    "financial": {
        "name": "💳 Financial Resources",
        "links": [
            ("Annual Credit Report", "https://www.annualcreditreport.com/"),
            ("CFPB", "https://www.consumerfinance.gov/"),
            ("Federal Reserve", "https://www.federalreserve.gov/"),
            ("FDIC BankFind", "https://banks.data.fdic.gov/bankfind-suite/")
        ]
    },
    "tools": {
        "name": "🛠 Online Tools",
        "links": [
            ("ICANN Lookup", "https://lookup.icann.org/"),
            ("URL Scanner", "https://urlscan.io/"),
            ("VirusTotal", "https://www.virustotal.com/"),
            ("Wayback Machine", "https://web.archive.org/")
        ]
    },
    "privacy": {
        "name": "🔐 Privacy & Security",
        "links": [
            ("Privacy Guides", "https://www.privacyguides.org/"),
            ("Electronic Frontier Foundation", "https://www.eff.org/"),
            ("Have I Been Pwned", "https://haveibeenpwned.com/"),
            ("Mozilla Monitor", "https://monitor.mozilla.org/")
        ]
    },
    "guides": {
        "name": "📚 Guides & Education",
        "links": [
            ("Google Search Help", "https://support.google.com/websearch/"),
            ("ICANN Learn", "https://learn.icann.org/"),
            ("FTC Consumer Advice", "https://consumer.ftc.gov/")
        ]
    }
}


def telegram(method, payload):
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing.")
        return None

    try:
        response = requests.post(
            f"{BASE_URL}/{method}",
            json=payload,
            timeout=15
        )
        result = response.json()

        if not result.get("ok"):
            logger.error("Telegram API error: %s", result)

        return result

    except requests.RequestException:
        logger.exception("Telegram request failed.")
        return None


def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = {
            "inline_keyboard": keyboard
        }

    return telegram("sendMessage", payload)


def edit_message(chat_id, message_id, text, keyboard):
    return telegram("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": keyboard
        }
    })


def answer_callback(callback_id):
    telegram("answerCallbackQuery", {
        "callback_query_id": callback_id
    })


def main_menu():
    buttons = []
    items = list(CATEGORIES.items())

    for i in range(0, len(items), 2):
        row = []

        for key, category in items[i:i + 2]:
            row.append({
                "text": category["name"],
                "callback_data": f"category:{key}"
            })

        buttons.append(row)

    buttons.append([
        {
            "text": "ℹ️ About",
            "callback_data": "about"
        },
        {
            "text": "❓ Help",
            "callback_data": "help"
        }
    ])

    return buttons


def category_menu(key):
    category = CATEGORIES[key]
    buttons = []

    for label, url in category["links"]:
        buttons.append([
            {
                "text": f"🔗 {label}",
                "url": url
            }
        ])

    buttons.append([
        {
            "text": "⬅️ Back to Main Menu",
            "callback_data": "home"
        }
    ])

    return buttons


def welcome_text():
    return (
        "🍔 BURGER CENTRE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Your central resource directory.\n\n"
        "Explore organized collections of "
        "search engines, public resources, "
        "business directories, research tools "
        "and educational references.\n\n"
        "Select a category below to get started.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BURGER CENTRE © 2026"
    )


def handle_command(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    command = text.split()[0].split("@")[0] if text else ""

    if command in ["/start", "/menu"]:
        send_message(
            chat_id,
            welcome_text(),
            main_menu()
        )

    elif command == "/help":
        send_message(
            chat_id,
            "🍔 BURGER CENTRE HELP\n\n"
            "/start — Open the welcome menu\n"
            "/menu — Open the resource directory\n"
            "/help — Display these instructions\n\n"
            "Select a category to explore its resources."
        )


def handle_callback(callback):
    answer_callback(callback["id"])

    data = callback.get("data", "")
    message = callback.get("message", {})

    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if not chat_id or not message_id:
        return

    if data == "home":
        edit_message(
            chat_id,
            message_id,
            welcome_text(),
            main_menu()
        )

    elif data == "about":
        edit_message(
            chat_id,
            message_id,
            "🍔 ABOUT BURGER CENTRE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Burger Centre is an organized "
            "directory of useful online resources, "
            "public information, search platforms, "
            "research tools and educational websites.\n\n"
            "Use resources responsibly and respect "
            "privacy and applicable laws.",
            [[{
                "text": "⬅️ Back to Main Menu",
                "callback_data": "home"
            }]]
        )

    elif data == "help":
        edit_message(
            chat_id,
            message_id,
            "❓ HOW TO USE BURGER CENTRE\n\n"
            "1. Select a category.\n"
            "2. Browse the available resources.\n"
            "3. Tap a link to open its website.\n"
            "4. Return to the main menu whenever needed.",
            [[{
                "text": "⬅️ Back to Main Menu",
                "callback_data": "home"
            }]]
        )

    elif data.startswith("category:"):
        key = data.split(":", 1)[1]

        if key in CATEGORIES:
            edit_message(
                chat_id,
                message_id,
                "🍔 BURGER CENTRE\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"{CATEGORIES[key]['name']}\n\n"
                "Select a resource below:",
                category_menu(key)
            )


@app.route("/")
def home():
    return "Burger Centre bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():

    if WEBHOOK_SECRET:
        supplied = request.headers.get(
            "X-Telegram-Bot-Api-Secret-Token", ""
        )

        if supplied != WEBHOOK_SECRET:
            return "Unauthorized", 401

    update = request.get_json(silent=True) or {}

    message = (
        update.get("message")
        or update.get("channel_post")
    )

    if message:
        handle_command(message)

    callback = update.get("callback_query")

    if callback:
        handle_callback(callback)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
