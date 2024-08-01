from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Ganti token dengan token bot Anda
TOKEN = '7139048077:AAE4AHcMbmfv0j80fAslQ3bo84syC3UbR-Y'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Bergabung dengan Grup", url='https://t.me/gacorgol')],
        [InlineKeyboardButton("Tutup", callback_data='close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Selamat datang! Bergabunglah pada grup dibawah ini untuk mendapatkan info Prediksi Bola Terbaru dan Terbaik!', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'close':
        await query.message.delete()

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
