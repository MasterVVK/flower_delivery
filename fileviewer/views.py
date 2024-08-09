from django.shortcuts import render
import os
import logging

logger = logging.getLogger('django')

# Список исключаемых файлов и папок
EXCLUDE_FILES_AND_DIRS = ['config.json', 'secret_folder', 'another_secret_file.txt']

def list_files(request, path=''):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Получить корневую директорию проекта
    target_dir = os.path.join(base_dir, path)
    files = []
    dirs = []
    try:
        for item in os.listdir(target_dir):
            item_path = os.path.join(path, item)  # Получить относительный путь
            if item in EXCLUDE_FILES_AND_DIRS or item_path in EXCLUDE_FILES_AND_DIRS:
                continue  # Исключить файлы и папки из списка
            if os.path.isfile(os.path.join(target_dir, item)):
                files.append(item)
            else:
                dirs.append(item)
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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Получить корневую директорию проекта
    file_path = os.path.join(base_dir, path)
    file_name = os.path.basename(file_path)
    logger.debug(f"Проверка файла: {file_path}")
    logger.debug(f"Базовый каталог: {base_dir}")
    logger.debug(f"Файл: {file_name}")
    if file_name in EXCLUDE_FILES_AND_DIRS or path in EXCLUDE_FILES_AND_DIRS:
        logger.debug(f"Доступ к файлу {file_name} запрещен.")
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
