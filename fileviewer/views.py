from django.shortcuts import render
import os

def list_files(request, path=''):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Получить корневую директорию проекта
    target_dir = os.path.join(base_dir, path)
    files = []
    dirs = []
    for item in os.listdir(target_dir):
        if item == 'config.json':
            continue  # Исключить config.json из списка
        if os.path.isfile(os.path.join(target_dir, item)):
            files.append(item)
        else:
            dirs.append(item)
    context = {
        'dirs': dirs,
        'files': files,
        'current_path': path,
    }
    return render(request, 'fileviewer/list_files.html', context)

def view_file(request, path):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Получить корневую директорию проекта
    file_path = os.path.join(base_dir, path)
    if 'config.json' in file_path:
        return render(request, 'fileviewer/not_allowed.html')  # Страница с сообщением о недоступности файла
    with open(file_path, 'r') as file:
        content = file.read()
    context = {
        'content': content,
        'file_path': path,
    }
    return render(request, 'fileviewer/view_file.html', context)
