import subprocess

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
            f'\n[Interface]\n'
            f'PrivateKey = {data["private_key"]}\n'
            f'Address = {data["address"]}\n'
            f'DNS = {data["dns"]}\n\n\n'
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
