import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.reply_to(message, "Hi, send me a link to a video from YouTube or Tik Tok\n")

@bot.message_handler(
    func=lambda message: "tiktok.com" in message.text or "youtube.com" in message.text or "youtu.be" in message.text)
def handle_video_request(message: Message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "Select format:", reply_markup=create_format_buttons(url))

def create_format_buttons(url):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("🎥 Video", callback_data=f"video|{url}"),
               InlineKeyboardButton("🎶 Audio", callback_data=f"audio|{url}"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def handle_format_selection(call):
    action, url = call.data.split('|')
    bot.answer_callback_query(call.id)

    if action == "video":
        bot.send_message(call.message.chat.id, "⏳ The video download has started...")
        download_and_send_media(call.message.chat.id, url, media_type='video')
    elif action == "audio":
        bot.send_message(call.message.chat.id, "⏳ The audio download has started...")
        download_and_send_media(call.message.chat.id, url, media_type='audio')

def download_and_send_media(chat_id, url, media_type='video'):
    if media_type == 'video':
        ydl_opts = {
            'format': 'best[ext=mp4]/best[ext=webm]',
            'outtmpl': 'downloads/%(title)s.%(ext)s'
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as file:
            if media_type == 'video':
                bot.send_video(chat_id, file, caption="🎥 Here's your video!")
            else:
                bot.send_audio(chat_id, file, caption="🎶 Here's your audio!")

        os.remove(filename)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    print("The bot is running")
    bot.infinity_polling()
