import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = '8503436459:AAFbCtsho5jS93J467v6rpxtIjseibXbj8Y'

async def download_content(url, mode):
    # مسح أي ملفات قديمة لتجنب تضارب الأسماء
    for f in ['file.mp4', 'file.mp3']:
        if os.path.exists(f): os.remove(f)

    if mode == 'video':
        ydl_opts = {
            'format': 'best[ext=mp4][filesize<45M]/best',
            'outtmpl': 'file.mp4'
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'file' # سيتم إنتاجه باسم file.mp3 تلقائياً
        }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await asyncio.to_thread(ydl.extract_info, url, download=True)
        return 'file.mp4' if mode == 'video' else 'file.mp3'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        context.user_data['url'] = url
        keyboard = [
            [InlineKeyboardButton("🎥 فيديو (MP4)", callback_data='video')],
            [InlineKeyboardButton("🎵 مقطع صوتي (MP3)", callback_data='audio')],
            [InlineKeyboardButton("🎤 رسالة صوتية (Voice)", callback_data='voice')]
        ]
        await update.message.reply_text("اختر الصيغة المطلوبة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data
    url = context.user_data.get('url')
    
    msg = await query.edit_message_text(f"⏳ جاري تجهيز {mode}... يرجى الانتظار")
    
    try:
        path = await download_content(url, mode)
        if not os.path.exists(path):
            raise Exception("لم يتم العثور على الملف المحمل")

        with open(path, 'rb') as f:
            if mode == 'video':
                await context.bot.send_video(chat_id=query.message.chat_id, video=f, write_timeout=600)
            elif mode == 'audio':
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, title="Audio MP3")
            elif mode == 'voice':
                await context.bot.send_voice(chat_id=query.message.chat_id, voice=f)
        
        os.remove(path)
        await msg.delete()
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ حدث خطأ: {e}")

if __name__ == '__main__':
    print("--- البوت الشامل يعمل الآن بنجاح ---")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
