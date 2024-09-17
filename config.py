# import json
# import os
# from datetime import datetime

# CONFIG_FILE = 'config.json'

# def load_config():
#     """Load configuration from the JSON file."""
#     if not os.path.exists(CONFIG_FILE):
#         return []

#     with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
#         try:
#             return json.load(file)
#         except json.JSONDecodeError as e:
#             print(f"Error reading {CONFIG_FILE}: {e}")
#             return []

# def save_config(directories):
#     """Save configuration to the JSON file."""
#     with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
#         json.dump(directories, file, ensure_ascii=False, indent=4)

# def time_to_str(time_str):
#     """Convert a time string in HH:MM format to a datetime.time object."""
#     try:
#         return datetime.strptime(time_str, '%H:%M').time()
#     except ValueError:
#         return None

# def str_to_time(time_obj):
#     """Convert a datetime.time object to a string in HH:MM format."""
#     return time_obj.strftime('%H:%M') if time_obj else "00:00"

# def update_last_checked(directories, path):
#     """Update the last checked time for a specific directory."""
#     for directory in directories:
#         if directory['path'] == path:
#             directory['last_checked'] = datetime.now().isoformat()
#             break
#     save_config(directories)

# def get_last_checked(directories, path):
#     """Get the last checked time for a specific directory."""
#     for directory in directories:
#         if directory['path'] == path:
#             return directory.get('last_checked', None)
#     return None

# def add_directory(directories, new_directory):
#     """Add a new directory to the configuration."""
#     directories.append(new_directory)
#     save_config(directories)

import json
import os
from datetime import datetime
import logging

# Конфигуриране на logging
logging.basicConfig(filename='config.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = 'config.json'

def load_config():
    """Зарежда конфигурацията от JSON файла."""
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"Файлът {CONFIG_FILE} не е намерен. Ще бъде създадена празна конфигурация.")
        return []
    
    logging.info(f"Опит за зареждане на конфигурацията от {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
        try:
            config_data = json.load(file)
            logging.info("Конфигурацията е заредена успешно.")
            return config_data
        except json.JSONDecodeError as e:
            logging.error(f"Грешка при четене на {CONFIG_FILE}: {e}")
            print(f"Грешка при четене на {CONFIG_FILE}: {e}")
            return []

def save_config(directories):
    """Запазва конфигурацията в JSON файла."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            json.dump(directories, file, ensure_ascii=False, indent=4)
        logging.info("Конфигурацията е запазена успешно.")
    except Exception as e:
        logging.error(f"Грешка при запазване на {CONFIG_FILE}: {e}")
        print(f"Грешка при запазване на {CONFIG_FILE}: {e}")

def time_to_str(time_str):
    """Convert a time string in HH:MM format to a datetime.time object."""
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        logging.error(f"Invalid time format: {time_str}")
        return None  # Връща None при грешка

def str_to_time(time_obj):
    """Convert a datetime.time object to a string in HH:MM format."""
    return time_obj.strftime('%H:%M') if time_obj else "00:00"

def update_last_checked(directories, path):
    """Update the last checked time for a specific directory."""
    for directory in directories:
        if directory['path'] == path:
            directory['last_checked'] = datetime.now().isoformat()
            break
    else: 
        logging.warning(f"Directory not found for update: {path}")
    try:
        save_config(directories)
    except Exception as e:  # Добавяме обработка на грешки при запазване
        logging.error(f"Грешка при обновяване на последно проверено време за {path}: {e}")

def get_last_checked(directories, path):
    """Get the last checked time for a specific directory."""
    for directory in directories:
        if directory['path'] == path:
            return directory.get('last_checked', None)
    return None

def add_directory(directories, new_directory):
    """Add a new directory to the configuration."""
    if any(d['path'] == new_directory['path'] for d in directories):
        print(f"Директорията {new_directory['path']} вече съществува!")
        logging.error(f"Directory already exists: {new_directory['path']}") 
    else:
        directories.append(new_directory)
        try:
            save_config(directories)
        except Exception as e: # Добавяме обработка на грешки при запазване
            logging.error(f"Грешка при добавяне на директория {new_directory['path']}: {e}")