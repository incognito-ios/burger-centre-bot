
import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
OWNER_ID = os.getenv("OWNER_ID")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# BURGER CENTRE RESOURCE DIRECTORY

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
        "name": "📩 2TT Mailer",
        "links": [
            ("2TT Mailer", "https://t.me/Mailer2TT_bot")
        ]
    },
    "financial": {
        "name": "🤖 TwoTT Bot",
        "links": [
            ("TwoTT Bot", "https://t.me/TwoTT_bot")
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


# TEMPORARY SUPPORT STATES

user_states = {}


def is_owner(user_id):
    return (
        OWNER_ID is not None
        and str(user_id) == str(OWNER_ID)
    )


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

    except (requests.RequestException, ValueError):
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


# DIRECTORY MENUS

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
        "text": "📩 Questions & Concerns",
        "callback_data": "support"
    }])

    buttons.append([{
        "text": "⚠️ Report an Error",
        "callback_data": "support:error"
    }])

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
        buttons.append([{
            "text": f"🔗 {label}",
            "url": url
        }])

    buttons.append([{
        "text": "⬅️ Back to Main Menu",
        "callback_data": "home"
    }])

    return buttons


def welcome_text():
    return (
        "🛸 BURGER CENTRE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "You made it to Burger Centre.\n\n"
        "Your portal to the other side of the internet.\n\n"
        "Explore bots, search engines, online tools, "
        "directories, research platforms and digital discoveries.\n\n"
        "Choose a department below to explore.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🧪 Explore the unknown.\n"
        "BURGER CENTRE © 2026"
    )


# SUPPORT SYSTEM

def start_support(chat_id, support_type):
    if support_type == "error":
        label = "ERROR REPORT"
    elif support_type == "concern":
        label = "CONCERN"
    else:
        label = "QUESTION"

    user_states[chat_id] = {
        "type": label
    }

    send_message(
        chat_id,
        "🛸 BURGER CENTRE // SUPPORT\n\n"
        f"Selected: {label}\n\n"
        "Please type your message below.\n\n"
        "For error reports, include what happened, "
        "which feature is affected, and any error message.\n\n"
        "An admin will review your submission.\n\n"
        "Send /cancel to cancel."
    )


def handle_support_message(message):
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    if text == "/cancel":
        user_states.pop(chat_id, None)
        send_message(chat_id, "Your submission has been cancelled.")
        return

    state = user_states.get(chat_id)

    if not state:
        return

    if not ADMIN_CHAT_ID:
        send_message(
            chat_id,
            "⚠️ The support desk is being configured. "
            "Please try again shortly."
        )
        return

    user = message.get("from", {})
    username = user.get("username")
    first_name = user.get("first_name", "Telegram user")

    user_label = f"@{username}" if username else first_name

    admin_text = (
        "🛸 BURGER CENTRE // NEW SUBMISSION\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Type: {state['type']}\n"
        f"From: {user_label}\n"
        f"User ID: {chat_id}\n\n"
        "MESSAGE:\n"
        f"{text}\n\n"
        f"BC_USER_ID:{chat_id}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Reply directly to this message to respond."
    )

    result = send_message(ADMIN_CHAT_ID, admin_text)

    if result and result.get("ok"):
        user_states.pop(chat_id, None)
        send_message(
            chat_id,
            "📡 TRANSMISSION RECEIVED\n\n"
            "Your submission has been delivered to "
            "the Burger Centre Admin Desk.\n\n"
            "An admin will respond when available.\n\n"
            "〘 ACCESS GRANTED 〙"
        )
    else:
        send_message(
            chat_id,
            "⚠️ Your submission could not be delivered. "
            "Please try again later."
        )


# OWNER-ONLY ADMIN REPLIES

def handle_admin_reply(message):
    chat_id = message.get("chat", {}).get("id")
    sender_id = message.get("from", {}).get("id")

    if not ADMIN_CHAT_ID or not OWNER_ID:
        return

    if str(chat_id) != str(ADMIN_CHAT_ID):
        return

    if not is_owner(sender_id):
        logger.warning("Unauthorized admin reply attempt.")
        return

    reply = message.get("reply_to_message")

    if not reply:
        return

    original_text = reply.get("text", "")
    marker = "BC_USER_ID:"

    if marker not in original_text:
        return

    try:
        target_id = int(
            original_text.split(marker, 1)[1].split()[0]
        )
    except (ValueError, IndexError):
        return

    response_text = message.get("text", "").strip()

    if not response_text:
        return

    result = send_message(
        target_id,
        "👽 BURGER CENTRE // ADMIN RESPONSE\n\n"
        f"{response_text}\n\n"
        "〘 TRANSMISSION COMPLETE 〙"
    )

    if result and result.get("ok"):
        send_message(chat_id, "📡 Response delivered.")
    else:
        send_message(
            chat_id,
            "⚠️ Could not deliver the response."
        )


# COMMAND HANDLER

def handle_command(message):
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    sender_id = message.get("from", {}).get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    command = text.split()[0].split("@")[0]

    # ID LOOKUP
    if command == "/getid":
        if chat.get("type") in ["group", "supergroup"]:
            send_message(
                chat_id,
                f"🛸 ADMIN DESK GROUP ID:\n{chat_id}"
            )
        else:
            send_message(
                chat_id,
                f"🛸 YOUR TELEGRAM USER ID:\n{sender_id}"
            )
        return

    # PRIVATE ADMIN CONTROLS
    if command in ["/admin", "/status"]:
        if not is_owner(sender_id):
            send_message(chat_id, "⛔ Access denied.")
            return

        if command == "/admin":
            send_message(
                chat_id,
                "🛸 BURGER CENTRE // ADMIN CONTROL\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "OWNER ACCESS GRANTED\n\n"
                "/status — System status\n"
                "/getid — Display your Telegram ID\n"
                "/menu — Open resource directory\n\n"
                "ADMIN DESK\n"
                "Submissions are delivered to your private group.\n"
                "Reply directly to a submission to contact its sender.\n\n"
                "〘 AUTHORIZED ACCESS ONLY 〙"
            )

        elif command == "/status":
            send_message(
                chat_id,
                "🛸 BURGER CENTRE // SYSTEM STATUS\n\n"
                f"Bot token: {'Configured' if BOT_TOKEN else 'Missing'}\n"
                f"Owner ID: {'Configured' if OWNER_ID else 'Missing'}\n"
                f"Admin Desk: {'Configured' if ADMIN_CHAT_ID else 'Missing'}\n"
                f"Categories: {len(CATEGORIES)}\n\n"
                "〘 SYSTEM CHECK COMPLETE 〙"
            )
        return

    # GROUP MESSAGES
    if chat.get("type") in ["group", "supergroup"]:
        if str(chat_id) == str(ADMIN_CHAT_ID):
            handle_admin_reply(message)
        return

    # PUBLIC BOT COMMANDS
    if command in ["/start", "/menu"]:
        user_states.pop(chat_id, None)
        send_message(
            chat_id,
            welcome_text(),
            main_menu()
        )

    elif command == "/help":
        send_message(
            chat_id,
            "🛸 BURGER CENTRE HELP\n\n"
            "/start — Open the welcome menu\n"
            "/menu — Open the resource directory\n"
            "/help — Display instructions\n"
            "/cancel — Cancel a support submission\n\n"
            "Use the support buttons for assistance."
        )

    elif command == "/cancel":
        user_states.pop(chat_id, None)
        send_message(chat_id, "Submission cancelled.")


# BUTTON HANDLER

def handle_callback(callback):
    answer_callback(callback["id"])

    data = callback.get("data", "")
    message = callback.get("message", {})

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    message_id = message.get("message_id")

    if not chat_id or not message_id:
        return

    if chat.get("type") != "private":
        send_message(
            chat_id,
            "Please open the Burger Centre bot privately "
            "to submit a support request."
        )
        return

    if data == "home":
        edit_message(
            chat_id,
            message_id,
            welcome_text(),
            main_menu()
        )

    elif data == "support":
        start_support(chat_id, "question")

    elif data == "support:error":
        start_support(chat_id, "error")

    elif data == "about":
        edit_message(
            chat_id,
            message_id,
            "🛸 ABOUT BURGER CENTRE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Burger Centre is a digital resource "
            "directory featuring useful online tools, "
            "bots, search platforms, public resources "
            "and educational references.\n\n"
            "Explore responsibly and respect privacy "
            "and applicable laws.",
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
            "2. Browse available resources.\n"
            "3. Tap a link to open it.\n"
            "4. Use support for assistance.",
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
                "🧪 BURGER CENTRE\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"{CATEGORIES[key]['name']}\n\n"
                "Select a resource below:",
                category_menu(key)
            )


# WEBHOOK

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
        chat_type = message.get("chat", {}).get("type")
        text = message.get("text", "").strip()

        if chat_type == "private":
            if text.startswith("/"):
                handle_command(message)
            else:
                handle_support_message(message)

        else:
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
