from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import OWNER_ID
from keys import generate_key, generate_public_key, generate_preshared_key, generate_config, get_unique_ip
from instructions import get_instruction_text
from tools import has_received_config, mark_as_received
import os
import subprocess

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Получить конфигурацию", callback_data='get_config')],
        [InlineKeyboardButton("Получить инструкцию", callback_data='choose_instruction')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Выберите, что вы хотите получить:',
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'get_config':
        if user_id != OWNER_ID and has_received_config(user_id):
            await query.message.reply_text("Вы уже получили конфигурацию.")
            return

        private_key = generate_key()
        if private_key is None:
            await query.message.reply_text("Ошибка генерации конфигурации.")
            return

        public_key = generate_public_key(private_key)
        if public_key is None:
            await query.message.reply_text("Ошибка генерации конфигурации.")
            return

        preshared_key = generate_preshared_key()
        if preshared_key is None:
            await query.message.reply_text("Ошибка генерации конфигурации.")
            return

        unique_ip_index = 21
        unique_ip = get_unique_ip(unique_ip_index)

        config_data = {
            'private_key': private_key,
            'address': unique_ip,
            'dns': '1.1.1.1',
            'public_key': public_key,
            'preshared_key': preshared_key,
            'allowed_ips': '0.0.0.0/0, ::/0',
            'persistent_keepalive': '0',
            'endpoint': '77.73.71.229:51820'
        }

        config = generate_config(config_data)
        if config is None:
            await query.message.reply_text("Ошибка генерации конфигурации.")
            return

        file_path = '/tmp/wg.conf'
        try:
            with open(file_path, 'w') as file:
                file.write(config)
        except IOError as e:
            await query.message.reply_text("Ошибка записи конфигурации.")
            print(f"Ошибка записи файла {file_path}: {e}")
            return

        try:
            with open(file_path, 'rb') as file:
                await query.message.reply_document(document=file, filename='wg.conf')
        except IOError as e:
            await query.message.reply_text("Ошибка отправки конфигурации.")
            print(f"Ошибка чтения файла {file_path}: {e}")

        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Ошибка удаления файла {file_path}: {e}")

        if user_id != OWNER_ID:
            mark_as_received(user_id)

    elif query.data == 'choose_instruction':
        keyboard = [
            [InlineKeyboardButton("iPhone", callback_data='instruction_iphone')],
            [InlineKeyboardButton("Android", callback_data='instruction_android')],
            [InlineKeyboardButton("Windows", callback_data='instruction_windows')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите вашу платформу:", reply_markup=reply_markup)

    elif query.data.startswith('instruction_'):
        instruction_text = get_instruction_text(query.data)
        await query.message.reply_text(instruction_text, parse_mode='MarkdownV2')

def main():
    application = Application.builder().token('7247112427:AAG1BH0P0KaATegVI8kzbd_RPcubNfQwA6M').build()  # Укажите ваш реальный токен бота
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.run_polling()

if __name__ == '__main__':
    main()
