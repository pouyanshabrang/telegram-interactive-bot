import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ⬇️ توکن ربات جدید خود را اینجا بین دابل کوتیشن بگذارید ⬇️
TOKEN = "8937575137:AAG73aaKzm8wtEiRPgYQc39aJzp_RVMtjhg"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
    await query.answer() # قطع کردن لودینگ تلگرام
    
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
    if not TOKEN or TOKEN == "توکن_جدید_خود_را_اینجا_بگذارید":
        print("لطفا توکن ربات را در متغیر TOKEN قرار دهید!")
        return
        
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("ربات با موفقیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
