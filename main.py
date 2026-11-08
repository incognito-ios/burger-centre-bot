
import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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
        "name": "📞 Phone & Email Lookup",
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
        "name": "📱 Social Media Search",
        "links": [
            ("Social Searcher", "https://www.social-searcher.com/"),
            ("Google Social Search", "https://www.google.com/search?q=social+media+profiles"),
            ("Namechk", "https://namechk.com/"),
            ("WhatsMyName", "https://whatsmyname.app/")
        ]
    },
    "images": {
        "name": "🖼 Image & Reverse Search",
        "links": [
            ("Google Lens", "https://lens.google.com/"),
            ("TinEye", "https://tineye.com/"),
            ("Bing Visual Search", "https://www.bing.com/visualsearch"),
            ("Yandex Images", "https://yandex.com/images/")
        ]
    },
    "maps": {
        "name": "📍 Maps & Location Tools",
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
            ("Whois Lookup", "https://lookup.icann.org/"),
            ("URL Scanner", "https://urlscan.io/"),
            ("VirusTotal", "https://www.virustotal.com/"),
            ("Wayback Machine", "https://web.archive.org/")
        ]
    },
    "privacy": {
        "name": "🔐 Privacy & Security",
        "links": [
            ("Privacy Guides", "https://www.privacyguides.org/"),
            ("EFF", "https://www.eff.org/"),
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


def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    return requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload,
        timeout=15
    )


def edit_message(chat_id, message_id, text, keyboard):
    return requests.post(
        f"{BASE_URL}/editMessageText",
        json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": {"inline_keyboard": keyboard}
        },
        timeout=15
    )


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

    buttons.append([{
        "text": "ℹ️ About Burger Centre",
        "callback_data": "about"
    }])

    return buttons


def category_menu(key):
    category = CATEGORIES[key]
    buttons = []

    for label, url in category["links"]:
        buttons.append([{"text": f"🔗 {label}", "url": url}])

    buttons.append([{
        "text": "⬅️ Back to Main Menu",
        "callback_data": "home"
    }])

    return buttons


def answer_callback(callback_id):
    requests.post(
        f"{BASE_URL}/answerCallbackQuery",
        json={"callback_query_id": callback_id},
        timeout=10
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

    message = update.get("message")
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if text in ["/start", "/menu"]:
            send_message(
                chat_id,
                "🍔 BURGER CENTRE\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Welcome to your resource hub.\n"
                "Choose a category below to explore useful links.",
                main_menu()
            )

        elif text == "/help":
            send_message(
                chat_id,
                "🍔 BURGER CENTRE HELP\n\n"
                "Use /start to open the main menu.\n"
                "Tap a category to see its resources."
            )

    callback = update.get("callback_query")
    if callback:
        answer_callback(callback["id"])
        data = callback.get("data", "")
        message = callback.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        if chat_id and message_id:
            if data == "home":
                edit_message(
                    chat_id,
                    message_id,
                    "🍔 BURGER CENTRE\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "Choose a resource category:",
                    main_menu()
                )

            elif data == "about":
                edit_message(
                    chat_id,
                    message_id,
                    "🍔 ABOUT BURGER CENTRE\n\n"
                    "A collection of useful public search "
                    "engines, directories, research tools, "
                    "and educational resources.\n\n"
                    "Use resources responsibly and respect "
                    "privacy and applicable laws.",
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
                        f"🍔 BURGER CENTRE\n"
                        f"━━━━━━━━━━━━━━━━━━\n\n"
                        f"{CATEGORIES[key]['name']}\n\n"
                        "Choose a resource:",
                        category_menu(key)
                    )

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
