from django.shortcuts import render
import os
import logging
import json
from pathlib import Path

logger = logging.getLogger('django')

# Загрузка конфигурации из config.json
BASE_DIR = Path(__file__).resolve().parent.parent
config_path = os.path.join(BASE_DIR, 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Список исключаемых файлов и папок
EXCLUDE_FILES_AND_DIRS = config.get('exclude_files_and_dirs', [])

def list_files(request, path=''):
    base_dir = '/srv/flower_delivery'  # Абсолютный путь к вашему проекту
    target_dir = os.path.join(base_dir, path)
    files = []
    dirs = []
    try:
        for item in os.listdir(target_dir):
            item_path = os.path.join(path, item)  # Получить относительный путь
            if item in EXCLUDE_FILES_AND_DIRS or item_path in EXCLUDE_FILES_AND_DIRS:
                continue  # Исключить файлы и папки из списка
            if os.path.isfile(os.path.join(target_dir, item)):
                files.append(item_path)
            else:
                dirs.append(item_path)
    except FileNotFoundError:
        logger.debug(f"Директория не найдена: {target_dir}")
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности папки
    context = {
        'dirs': dirs,
        'files': files,
        'current_path': path,
    }
    return render(request, 'fileviewer/list_files.html', context)

def view_file(request, path):
    base_dir = '/srv/flower_delivery'  # Абсолютный путь к вашему проекту
    file_path = os.path.join(base_dir, path)
    logger.debug(f"Проверка файла: {file_path}")
    if os.path.basename(file_path) in EXCLUDE_FILES_AND_DIRS:
        logger.debug(f"Доступ к файлу {file_path} запрещен.")
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.debug(f"Файл не найден: {file_path}")
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    except PermissionError:
        logger.debug(f"Нет прав доступа к файлу: {file_path}")
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    except Exception as e:
        logger.debug(f"Ошибка при открытии файла: {file_path}, {e}")
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    context = {
        'content': content,
        'file_path': path,
    }
    return render(request, 'fileviewer/view_file.html', context)
