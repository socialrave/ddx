def get_instruction_text(query_data):
    if query_data == 'instruction_iphone':
        return (
            "Скачай __[приложение](https://apps\\.apple\\.com/ru/app/wireguard/id1441195209)__ \n"
             "Открой приложение и нажмите на '\\+' для добавления новой конфигурации\n"
             "Вставь конфигурационный файл\n"
             "Активируй VPN"
        )
    elif query_data == 'instruction_android':
        return (
            "Скачай __[приложение](https://play\\.google\\.com/store/apps/details\\?id=com\\.wireguard\\.android)__ \n"
             "Открой приложение и нажмите на '\\+' для добавления новой конфигурации\n"
             "Импортируй конфигурационный файл\\.\n"
             "Активируй VPN"
        )
    elif query_data == 'instruction_windows':
        return (
            "Скачай и установи __[приложение](https://www\\.wireguard\\.com/install/)__ с официального сайта\n"
             "Открой приложение\\, нажми \\- добавить туннель и импортируй конфигурационный файл\n"
             "Подключись к VPN через приложение"
        )
