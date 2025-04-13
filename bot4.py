import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
# Logging
logging.basicConfig(level=logging.INFO)

# Bot tokeningizni shu yerga yozing


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Matn xabarlar uchun handler
@dp.message_handler(content_types=types.ContentType.TEXT)
async def translate_text(message: types.Message):
    if message.chat.type in ['group', 'supergroup']:
        try:
            translated = GoogleTranslator(source='uz', target='ar').translate(message.text)

            # Arabcha audio yaratish
            tts = gTTS(text=translated, lang='ar')
            audio_path = f"{message.message_id}_text_ar.mp3"
            tts.save(audio_path)

            await message.reply(f"🇸🇦 Arabchaga tarjima:\n{translated}")
            with open(audio_path, 'rb') as audio_file:
                await message.reply_voice(audio_file, caption="🔊 Arabcha audio")

            os.remove(audio_path)

        except Exception as e:
            await message.reply("❌ Tarjima yoki audio yaratishda xatolik bo‘ldi.")
            print("Matn xatosi:", e)

# Ovozli xabarlar uchun handler
@dp.message_handler(content_types=types.ContentType.VOICE)
async def voice_handler(message: types.Message):
    try:
        file_id = message.voice.file_id
        voice = await bot.get_file(file_id)
        file_path = voice.file_path
        await bot.download_file(file_path, 'voice.ogg')

        # OGG -> WAV
        audio = AudioSegment.from_file("voice.ogg")
        audio.export("voice.wav", format="wav")

        # Ovoz -> Matn
        recognizer = sr.Recognizer()
        with sr.AudioFile("voice.wav") as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="uz-UZ")

        # Matn -> Arab tiliga tarjima
        translated = GoogleTranslator(source='uz', target='ar').translate(text)

        # Arabcha audio
        tts = gTTS(text=translated, lang='ar')
        audio_path = f"{message.message_id}_voice_ar.mp3"
        tts.save(audio_path)

        await message.reply(f"📝 Tanilgan matn: {text}\n\n🇸🇦 Arabchaga tarjima:\n{translated}")
        with open(audio_path, 'rb') as audio_file:
            await message.reply_voice(audio_file, caption="🔊 Arabcha audio")

        # Tozalash
        os.remove("voice.ogg")
        os.remove("voice.wav")
        os.remove(audio_path)

    except Exception as e:
        await message.reply("❌ Ovozli tarjima amalga oshmadi.")
        print("Ovoz xatosi:", e)

# Ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
