import os
from pathlib import Path

def print_directory_structure(root_dir, prefix=""):
    """
    Рекурсивно выводит структуру директорий и файлов, разделенную по уровням.

    Args:
        root_dir (str): Корневая директория для обхода.
        prefix (str): Префикс для форматирования вывода (используется для рекурсии).
    """
    try:
        # Получаем список файлов и папок в текущей директории
        items = os.listdir(root_dir)
        items.sort()  # Сортируем для упорядоченного вывода

        for i, item in enumerate(items):
            # Полный путь к текущему элементу
            item_path = os.path.join(root_dir, item)

            # Определяем, является ли элемент файлом или папкой
            if os.path.isdir(item_path):
                # Если это папка, выводим ее имя
                print(f"{prefix}├── {item}/")
                # Рекурсивно вызываем функцию для поддиректории
                if i == len(items) - 1:
                    print_directory_structure(item_path, prefix + "    ")
                else:
                    print_directory_structure(item_path, prefix + "│   ")
            else:
                # Если это файл, выводим его имя
                if i == len(items) - 1:
                    print(f"{prefix}└── {item}")
                else:
                    print(f"{prefix}├── {item}")
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
    except FileNotFoundError:
        print(f"{prefix}└── [Directory not found]")

# Пример использования
if __name__ == "__main__":
    root_directory = Path('..').absolute()
    print_directory_structure(root_directory)