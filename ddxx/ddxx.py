from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import subprocess
import os

# Ваш уникальный ID пользователя
OWNER_ID = 94163524  # Замените на ваш реальный ID

# Функции генерации ключей и конфигурации
def generate_key():
    try:
        return subprocess.check_output(['wg', 'genkey']).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка генерации ключа: {e}")
        return None

def generate_public_key(private_key):
    try:
        return subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка генерации публичного ключа: {e}")
        return None

def generate_preshared_key():
    try:
        return subprocess.check_output(['wg', 'genpsk']).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка генерации пресшаред ключа: {e}")
        return None

def generate_config(data):
    try:
        return (
            f'[Interface]\n'
            f'PrivateKey = {data["private_key"]}\n'
            f'Address = {data["address"]}\n'
            f'DNS = {data["dns"]}\n\n'
            f'[Peer]\n'
            f'PublicKey = {data["public_key"]}\n'
            f'PresharedKey = {data["preshared_key"]}\n'
            f'AllowedIPs = {data["allowed_ips"]}\n'
            f'PersistentKeepalive = {data["persistent_keepalive"]}\n'
            f'Endpoint = {data["endpoint"]}'
        )
    except KeyError as e:
        print(f"Ошибка в данных конфигурации: {e}")
        return None

def get_unique_ip(index):
    base_ip = "10.8.0."
    return f'{base_ip}{index}/24'

def has_received_config(user_id):
    file_path = 'users_data.txt'
    try:
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as file:
            received_users = file.read().splitlines()
        return str(user_id) in received_users
    except IOError as e:
        print(f"Ошибка чтения файла {file_path}: {e}")
        return False

def mark_as_received(user_id):
    file_path = 'users_data.txt'
    try:
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        with open(file_path, 'a') as file:
            file.write(f"{user_id}\n")
    except IOError as e:
        print(f"Ошибка записи в файл {file_path}: {e}")

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
        
        # Генерация ключей и конфигурации
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

        # Пример уникального IP-адреса (для примера используем 21)
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

        # Запись конфигурации в файл
        file_path = '/tmp/wg.conf'
        try:
            with open(file_path, 'w') as file:
                file.write(config)
        except IOError as e:
            await query.message.reply_text("Ошибка записи конфигурации.")
            print(f"Ошибка записи файла {file_path}: {e}")
            return

        # Отправка файла пользователю
        try:
            with open(file_path, 'rb') as file:
                await query.message.reply_document(document=file, filename='wg.conf')
        except IOError as e:
            await query.message.reply_text("Ошибка отправки конфигурации.")
            print(f"Ошибка чтения файла {file_path}: {e}")

        # Удаление временного файла
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Ошибка удаления файла {file_path}: {e}")

        # Запись пользователя в файл, если это не создатель
        if user_id != OWNER_ID:
            mark_as_received(user_id)

    elif query.data == 'choose_instruction':
        # Показать кнопки для выбора платформы
        keyboard = [
            [InlineKeyboardButton("iPhone", callback_data='instruction_iphone')],
            [InlineKeyboardButton("Android", callback_data='instruction_android')],
            [InlineKeyboardButton("Windows", callback_data='instruction_windows')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите вашу платформу:", reply_markup=reply_markup)

    elif query.data.startswith('instruction_'):
        if query.data == 'instruction_iphone':
            # Инструкция для iPhone
            instruction_text = (
                "Скачай __[приложение](https://apps\\.apple\\.com/ru/app/wireguard/id1441195209)__ \n"
                "Открой приложение и нажмите на '\\+' для добавления новой конфигурации\n"
                "Вставь конфигурационный файл\n"
                "Активируй VPN"
            )
        elif query.data == 'instruction_android':
            # Инструкция для Android
            instruction_text = (
                "Скачай __[приложение](https://play\\.google\\.com/store/apps/details\\?id=com\\.wireguard\\.android)__ \n"
                "Открой приложение и нажмите на '\\+' для добавления новой конфигурации\n"
                "Импортируй конфигурационный файл\\.\n"
                "Активируй VPN"
            )
        elif query.data == 'instruction_windows':
            # Инструкция для Windows
            instruction_text = (
                "Скачай и установи __[приложение](https://www\\.wireguard\\.com/install/)__ с официального сайта\n"
                "Открой приложение\\, нажми \\- добавить туннель и импортируй конфигурационный файл\n"
                "Подключись к VPN через приложение"
            )

        await query.message.reply_text(instruction_text, parse_mode='MarkdownV2')

def main():
    application = Application.builder().token('7247112427:AAG1BH0P0KaATegVI8kzbd_RPcubNfQwA6M').build()  # Укажите ваш реальный токен бота
    
    # Добавляем обработчики команд и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
