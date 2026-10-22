import logging
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# خواندن توکن از متغیر محیطی Render
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- وب‌سرور ساده برای اینکه Render فکر نکند برنامه خراب است ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()

# --- کدهای ربات تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌐 به ربات ایران و جهان خبر خوش آمدید!\n\n"
        "📰 اخبار ایران و جهان\n"
        "💱 ارزهای رایج و ارزهای دیجیتال\n"
        "📈 بورس جهانی\n\n"
        "برای دیدن منو روی /menu کلیک کنید."
    )
    await update.message.reply_text(text)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌍 اخبار کشورها", callback_data="countries"),
         InlineKeyboardButton("📰 آخرین اخبار", callback_data="latest_news")],
        [InlineKeyboardButton("⚽ ورزش", callback_data="sports"),
         InlineKeyboardButton("💹 ارزهای رایج", callback_data="currencies")],
        [InlineKeyboardButton("📈 بورس جهانی", callback_data="stocks"),
         InlineKeyboardButton("📱 ارز دیجیتال", callback_data="crypto")],
        [InlineKeyboardButton("⚙️ تنظیمات اخبار من", callback_data="settings"),
         InlineKeyboardButton("🔔 اعلان‌ها", callback_data="notifications")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🌐 منوی اصلی ایران و جهان خبر\n\nلطفاً یکی از بخش‌های زیر را انتخاب کن:"
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "countries":
        keyboard = [
            [InlineKeyboardButton("🇮🇷 ایران", callback_data="news_iran"),
             InlineKeyboardButton("🇺🇸 آمریکا", callback_data="news_usa")],
            [InlineKeyboardButton("🇮🇱 اسرائیل", callback_data="news_israel"),
             InlineKeyboardButton("🌍 خاورمیانه", callback_data="news_mideast")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]
        ]
        await query.edit_message_text("🌍 لطفاً کشور یا منطقه مورد نظر خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "back_to_menu":
        keyboard = [
            [InlineKeyboardButton("🌍 اخبار کشورها", callback_data="countries"),
             InlineKeyboardButton("📰 آخرین اخبار", callback_data="latest_news")],
            [InlineKeyboardButton("⚽ ورزش", callback_data="sports"),
             InlineKeyboardButton("💹 ارزهای رایج", callback_data="currencies")],
            [InlineKeyboardButton("📈 بورس جهانی", callback_data="stocks"),
             InlineKeyboardButton("📱 ارز دیجیتال", callback_data="crypto")],
            [InlineKeyboardButton("⚙️ تنظیمات اخبار من", callback_data="settings"),
             InlineKeyboardButton("🔔 اعلان‌ها", callback_data="notifications")]
        ]
        await query.edit_message_text("🌐 منوی اصلی ایران و جهان خبر\n\nلطفاً یکی از بخش‌های زیر را انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "latest_news":
        await query.edit_message_text("در حال دریافت آخرین اخبار...")
        try:
            response = requests.get("https://feeds.bbci.co.uk/persian/rss.xml", timeout=5)
            response.raise_for_status()
            items = response.text.split("<item>")
            if len(items) > 1:
                item = items[1]
                title = item.split("<title>", 1)[1].split("</title>", 1)[0].replace("<![CDATA[", "").replace("]]>", "")
                link = item.split("<link>", 1)[1].split("</link>", 1)[0].replace("<![CDATA[", "").replace("]]>", "")
                await query.message.reply_text(f"📰 {title}\n\n🔗 لینک خبر:\n{link}")
            else:
                await query.message.reply_text("خطا: خبری یافت نشد.")
        except Exception as e:
            await query.message.reply_text("خطا در دریافت خبر.")
            
    else:
        await query.message.reply_text(f"بخش «{query.data}» به‌زودی اضافه می‌شود.")

def main():
    # اجرای وب‌سرور در یک ترد جداگانه تا Render راضی باشد
    threading.Thread(target=run_web_server, daemon=True).start()
    
    if not TOKEN:
        print("خطا: توکن ربات در متغیرهای محیطی (BOT_TOKEN) یافت نشد!")
        return
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("ربات با موفقیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
