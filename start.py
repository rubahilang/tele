from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import json
import logging

# Bot token
TOKEN = '7073207315:AAG1UUyjXt5eDSXWd5K20A3pmZ_QeuO_sZU'
GROUP_ID = '@gacorgol'  # ID grup Telegram yang harus diikuti
GROUP_LINK = 'https://t.me/gacorgol'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Paths to JSON files
USER_JSON_PATH = 'user.json'
GROUP_JSON_PATH = 'groups.json'

# Load or initialize user list
def load_users_from_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Data is not in expected format")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        data = {}
    return data

# Function to save users to file
def save_users_to_file(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load groups from file
def load_groups_from_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

# Function to save groups to file
def save_groups_to_file(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# Function to handle /start command
async def start(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username if update.message.from_user.username else "unknown"
    
    # Check if the user has joined the group
    try:
        chat_member = await context.bot.get_chat_member(chat_id=GROUP_ID, user_id=update.message.from_user.id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            users = load_users_from_file(USER_JSON_PATH)
            
            if context.args:
                referrer_username = context.args[0]
                if referrer_username in users:
                    if username not in users[referrer_username].get('referrals', []):
                        users[username] = {'balance': 10000, 'referrals': [], 'referred_by': referrer_username}
                        users[referrer_username]['balance'] += 2000
                        if username not in users[referrer_username]['referrals']:
                            users[referrer_username]['referrals'].append(username)
                        save_users_to_file(USER_JSON_PATH, users)
                        
                        # Send a message to the referrer
                        try:
                            referrer_chat_member = await context.bot.get_chat_member(chat_id=GROUP_ID, user_id=update.message.from_user.id)
                            referrer_user_id = referrer_chat_member.user.id
                            
                            await context.bot.send_message(
                                chat_id=referrer_user_id,
                                text=f'Selamat! {username} telah bergabung menggunakan referral Anda.'
                            )
                            
                        except Exception as e:
                            logging.error(f'Failed to send message to referrer: {e}')
                        
                        await update.message.reply_text(f'Selamat! Anda telah bergabung menggunakan referral {referrer_username}. Saldo {referrer_username} telah ditambahkan 2000.')
                    else:
                        await update.message.reply_text('Anda sudah menggunakan referral ini.')
                else:
                    await update.message.reply_text('Referrer tidak valid.')
            else:
                users[username] = {'balance': 10000, 'referrals': []}
                save_users_to_file(USER_JSON_PATH, users)
                await update.message.reply_text('Selamat datang!')

            # Show the options with styled buttons
            keyboard = [
                [InlineKeyboardButton("Tampilkan Penghasilan", callback_data='show_balance'),
                 InlineKeyboardButton("Dapatkan Referral Link", callback_data=f'referral_{username}')],
                [InlineKeyboardButton("Total Referral", callback_data='total_referral'),
                 InlineKeyboardButton("Tarik Uang", callback_data='withdraw')],
                [InlineKeyboardButton("Ladang Cuan", callback_data='ladang_cuan')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Pilih opsi:', reply_markup=reply_markup)
        else:
            await update.message.reply_text(
                f'Anda harus bergabung dengan grup ini terlebih dahulu sebelum menggunakan bot: {GROUP_LINK}'
            )
            
            # Check if user used referral and hasn't joined the group yet
            users = load_users_from_file(USER_JSON_PATH)
            referrer = next((u for u, v in users.items() if v.get('referrals') and username in v['referrals']), None)
            if referrer:
                referral_link = f'https://t.me/CUAN_WINGAMING_BOT?start={referrer}'
                keyboard = [
                    [InlineKeyboardButton("Mulai Ulang", callback_data=f'reset_{referrer}')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    'Anda harus bergabung dengan grup terlebih dahulu untuk menggunakan bot. '
                    'Jika Anda bergabung melalui referral, Anda dapat memulai ulang proses dengan tombol di bawah ini.',
                    reply_markup=reply_markup
                )
    except Exception as e:
        logging.error(f'Error checking group membership: {e}')
        await update.message.reply_text('Terjadi kesalahan saat memeriksa keanggotaan grup.')

# Function to handle button presses
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    username = query.from_user.username if query.from_user.username else "unknown"

    if not is_user_in_user_js(username):
        await query.message.reply_text(f'Anda harus bergabung dengan grup ini terlebih dahulu sebelum menggunakan fitur bot: {GROUP_LINK}')
        return

    # Handle button presses
    if query.data == 'show_balance':
        balance = get_user_balance(username)
        await query.message.reply_text(f'Saldo Anda adalah {balance}')
    elif query.data.startswith('referral_'):
        referrer_username = query.data.split('_', 1)[1]
        referral_link = f'https://t.me/CUAN_WINGAMING_BOT?start={referrer_username}'
        await query.message.reply_text(
            f'🚀 DANA KAGET X WINGAMING77🚀\n\n'
            f'Ini dia kesempatan emas untuk meraih cuan dengan cara yang seru dan menguntungkan! 💰✨ Bergabunglah dengan bot penghasil cuan kami dan rasakan sendiri keuntungannya!\n\n'
            f'Daftar sekarang lewat link ini:\n'
            f'⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️\n'
            f'{referral_link} 🎯🔗\n'
            f'⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️\n'
            f'dan mulai perjalanan Anda menuju cuan yang melimpah! 🎉💸\n\n'
            f'Jangan lewatkan peluang langka ini! 💎 Segera daftar dan buktikan sendiri betapa mudahnya menghasilkan uang. 💵🔥 Ajak teman-teman Anda juga, dan nikmati hasilnya bersama! 👯‍♂️🙌\n\n'
            f'Kesempatan ini hanya datang sekali—ambil langkah pertama Anda sekarang juga! 🚀💥'
        )
    elif query.data == 'total_referral':
        total_referrals = get_total_referrals(username)
        await query.message.reply_text(f'Jumlah referral Anda adalah {total_referrals}')
    elif query.data == 'withdraw':
        await query.message.reply_text(
            f"!----------------------------------------------!\n"
            f'Saldo saat ini Rp. {get_user_balance(username)}\n'
            'Untuk penarikan minimal 50.000\n'
            'Ketik Format: TARIK Nominal NO-DANA\n'
            'Contoh: TARIK 50000 081234567890\n'
            f"!----------------------------------------------!\n"
        )
    elif query.data == 'ladang_cuan':
        await query.message.reply_text(
            "Ingin mendapatkan penghasilan tanpa batas? Dapatkan informasi lebih lanjut dengan mengunjungi:\n"
            "https://rebrand.ly/winsolution"
        )
    elif query.data.startswith('reset_'):
        referrer_username = query.data.split('_', 1)[1]
        users = load_users_from_file(USER_JSON_PATH)
        if username in users:
            users[username]['balance'] = 10000
            save_users_to_file(USER_JSON_PATH, users)
            referral_link = f'https://t.me/CUAN_WINGAMING_BOT?start={referrer_username}'
            await query.message.reply_text(
                'Data Anda telah di-reset. Silakan jalankan perintah /start untuk memulai kembali.\n'
                f'Gunakan link referral berikut: {referral_link}'
            )
        else:
            await query.message.reply_text('Anda tidak terdaftar dalam sistem.')

# Function to get user balance
def get_user_balance(username: str) -> int:
    users = load_users_from_file(USER_JSON_PATH)
    return users.get(username, {}).get('balance', 0)

# Function to get total referrals
def get_total_referrals(username: str) -> int:
    users = load_users_from_file(USER_JSON_PATH)
    return len(users.get(username, {}).get('referrals', []))

# Function to check if user is in user.js
def is_user_in_user_js(username: str) -> bool:
    users = load_users_from_file(USER_JSON_PATH)
    return username in users

# Function to handle text messages for withdrawals
async def handle_text_message(update: Update, context: CallbackContext) -> None:
    # Check if the message is from a private chat
    if update.message.chat.type != 'private':
        return

    text = update.message.text
    username = update.message.from_user.username if update.message.from_user.username else "unknown"

    if not is_user_in_user_js(username):
        await update.message.reply_text(f'Anda harus bergabung dengan grup ini terlebih dahulu sebelum menggunakan fitur bot: {GROUP_LINK}')
        return

    if text.startswith('TARIK'):
        parts = text.split()
        if len(parts) != 3:
            await update.message.reply_text('Format penarikan salah. Gunakan format: TARIK {jumlah} {nomor_dana}')
            return

        try:
            amount = int(parts[1])
            dana_number = parts[2]
        except ValueError:
            await update.message.reply_text('Jumlah harus berupa angka.')
            return

        if amount < 50000:
            await update.message.reply_text('Jumlah penarikan minimal adalah 50.000.')
            return

        balance = get_user_balance(username)

        if amount > balance:
            await update.message.reply_text('Saldo Anda tidak mencukupi untuk penarikan ini.')
            return

        # Format the withdrawal message
        withdrawal_message = (
            "!----------------------------------------------!\n"
            "💸Penarikan Berhasil💸\n"
            f"Username: {username}\n"
            f"Jumlah: {amount}\n"
            f"Nomor Dana: {dana_number}\n"
            f"Sisa Saldo: {balance - amount}\n"
            "Status: Pending\n"
            "!----------------------------------------------!"
        )

        # Send the withdrawal message
        await update.message.reply_text(withdrawal_message)

        # Update the user's balance
        update_user_balance(username, balance - amount)

# Function to update user balance
def update_user_balance(username: str, new_balance: int) -> None:
    users = load_users_from_file(USER_JSON_PATH)
    if username in users:
        users[username]['balance'] = new_balance
        save_users_to_file(USER_JSON_PATH, users)

# Main function to start the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until you send a signal to stop
    application.run_polling()

if __name__ == '__main__':
    main()
