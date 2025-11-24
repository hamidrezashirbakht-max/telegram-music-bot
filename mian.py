import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests

BOT_TOKEN = "8254046926:AAHiHFZdqDSI9R0KUMAedG1S3YRyqlSJRa4"
API_KEY = "kdYEojQZ-Gjk_azJn0PM05AFBghjicsA7rx0UroXaAcMYE1E5Z_OHBnm_MGmbrFY"

logging.basicConfig(level=logging.INFO)

def get_lyrics_and_translate(song_name):
    try:
        url = f"https://api.musixmatch.com/ws/1.1/track.search?q_track={song_name}&apikey={API_KEY}"
        data = requests.get(url).json()

        track_list = data["message"]["body"]["track_list"]
        if not track_list:
            return "متن آهنگ پیدا نشد.", ""

        track_id = track_list[0]["track"]["track_id"]

        url2 = f"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={API_KEY}"
        data2 = requests.get(url2).json()

        lyrics = data2["message"]["body"]["lyrics"]["lyrics_body"]

        translate_res = requests.post(
            "https://api.mymemory.translated.net/get",
            params={"q": lyrics, "langpair": "en|fa"}
        ).json()["responseData"]["translatedText"]

        return lyrics, translate_res

    except Exception as e:
        return f"خطا : {e}", ""

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.audio.get_file()
    await file.download_to_drive("song.mp3")

    await update.message.reply_text("آهنگ دریافت شد! در حال پردازش...")

    song_name = update.message.audio.title or "unknown"

    lyrics, translation = get_lyrics_and_translate(song_name)

    await update.message.reply_text(f"🎵 نام آهنگ:\n{song_name}")
    await update.message.reply_text(f"📄 متن آهنگ:\n{lyrics}")
    await update.message.reply_text(f"🇮🇷 ترجمه:\n{translation}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_name = update.message.text
    await update.message.reply_text("در حال جستجوی متن آهنگ...")

    lyrics, translation = get_lyrics_and_translate(song_name)

    await update.message.reply_text(f"📄 متن آهنگ:\n{lyrics}")
    await update.message.reply_text(f"🇮🇷 ترجمه:\n{translation}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
