import re
from pyrogram import Client, filters
from pyrogram.types import Message
import phonenumbers
from phonenumbers import geocoder, timezone
import pycountry

# 🔐 Replace these with your Telegram API credentials
API_ID = 23076905
API_HASH = "b7720ee893ff1fdc3ea15132e63d5e0b"
BOT_TOKEN = "8313906278:AAFsA6Vak4cCiyoOHMPMclLnczkU-dXQng4"

# Known languages map
known_languages = {
    "Bangladesh": "Bengali",
    "India": "Hindi / English",
    "Pakistan": "Urdu",
    "Afghanistan": "Pashto / Dari",
    "United States": "English",
    "United Kingdom": "English",
    "Saudi Arabia": "Arabic",
    "Russia": "Russian",
    "Germany": "German",
    "France": "French",
    "Japan": "Japanese",
    "China": "Mandarin Chinese",
    "Brazil": "Portuguese",
    "Indonesia": "Indonesian",
    "Spain": "Spanish",
    "Italy": "Italian",
    "Canada": "English / French",
    "Mexico": "Spanish",
    "Turkey": "Turkish",
    "Vietnam": "Vietnamese",
    "South Korea": "Korean",
    "Thailand": "Thai",
    "South Africa": "Zulu / Afrikaans / English",
    "Egypt": "Arabic",
    "Nigeria": "English",
    "Argentina": "Spanish",
    "Philippines": "Filipino / English",
    "Iran": "Persian",
    "Iraq": "Arabic / Kurdish",
    "Malaysia": "Malay",
    "Ukraine": "Ukrainian",
    "Poland": "Polish",
    "Netherlands": "Dutch",
    "Australia": "English",
}

bot = Client("number_info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    await message.reply_text("👋 Welcome! Just send any phone number (with or without +) to get full details.")

@bot.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def number_info(_, message: Message):
    number_raw = message.text.strip()

    if not re.fullmatch(r"[\d+]+", number_raw):
        await message.reply_text("❌ Please enter a valid phone number (digits only).")
        return

    if not number_raw.startswith("+"):
        number_raw = "+" + number_raw

    try:
        number_obj = phonenumbers.parse(number_raw)

        if not phonenumbers.is_valid_number(number_obj):
            raise Exception("Invalid")

        number_format = phonenumbers.format_number(number_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        country = geocoder.description_for_number(number_obj, "en")
        region_code = number_obj.country_code
        timezones = timezone.time_zones_for_number(number_obj)
        language = known_languages.get(country, "Unknown")

        message_text = (
            f"📞 Number: {number_format}\n"
            f"🌍 Country: {country}\n"
            f"🗣️ Language: {language}\n"
            f"🕒 Timezone: {', '.join(timezones)}\n"
            f"🔢 Country Code: +{region_code}"
        )

    except:
        message_text = "❌ Sorry, this number is invalid or not recognized. Please try again with a correct number."

    await message.reply_text(message_text)

bot.run()