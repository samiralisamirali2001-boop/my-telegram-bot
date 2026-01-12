import telebot
import yt_dlp
import os
import time

# ضع التوكن الجديد هنا
API_TOKEN = '8503436459:AAFbCtsho5jS93J467v6rpxtIjseibXbj8Y'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✨ أهلاً بك! أنا بوت تحميل الفيديوهات.\n\nفقط أرسل لي رابط الفيديو من (YouTube, Instagram, TikTok) وسأقوم بتحميله لك فوراً! 🚀")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "http" not in url:
        return

    msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل... انتظر قليلاً.")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}", message.chat.id, msg.message_id)

# ميزة المحاولة التلقائية لتجنب أخطاء الاتصال
while True:
    try:
        print("Bot is starting...")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Error occurred: {e}. Restarting in 5 seconds...")
        time.sleep(5)
