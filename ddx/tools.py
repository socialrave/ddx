import os

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
