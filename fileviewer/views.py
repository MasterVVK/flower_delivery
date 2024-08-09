from django.shortcuts import render
import os

# Список исключаемых файлов и папок
EXCLUDE_FILES_AND_DIRS = ['config.json', 'secret_folder', 'another_secret_file.txt']

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
                files.append(item)
            else:
                dirs.append(item)
    except FileNotFoundError:
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
    file_name = os.path.basename(file_path)
    if file_name in EXCLUDE_FILES_AND_DIRS or path in EXCLUDE_FILES_AND_DIRS:
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    context = {
        'content': content,
        'file_path': path,
    }
    return render(request, 'fileviewer/view_file.html', context)
