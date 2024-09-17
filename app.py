# import tkinter as tk
# from gui.main_window import MainWindow
# from gui.notification_window import NotificationWindow
# from watcher import DirectoryWatcher
# from config import load_config, save_config, add_directory, update_last_checked, get_last_checked

# def main():
#     root = tk.Tk()
#     root.title("File Watcher")

#     directories = load_config()

#     watcher = None

#     # Създаване на независим прозорец за нотификации
#     notification_window = NotificationWindow(master=root)

#     def start_watching():
#         nonlocal watcher
#         if watcher is None:
#             watcher = DirectoryWatcher(directories, notification_window.add_notification)
#             watcher.start_watching()

#     def stop_watching():
#         nonlocal watcher
#         if watcher is not None:
#             watcher.stop_watching()
#             watcher = None

#     def edit_directory(directory):
#         # Функция за редактиране на директория
#         save_config(directories)

#     def delete_directory(directory):
#         # Функция за изтриване на директория
#         directories.remove(directory)
#         save_config(directories)
#         app.update_directory_list(directories)

#     def add_directory_callback(new_directory):
#         # Функция за добавяне на нова директория
#         add_directory(directories, new_directory)
#         app.update_directory_list(directories)

#     # Основен прозорец
#     app = MainWindow(root, directories, start_watching, stop_watching, edit_directory, delete_directory, add_directory_callback)

#     # Показване на прозореца за нотификации
#     notification_window.show()

#     root.mainloop()

# if __name__ == "__main__":
#     main()


# 30/08/2024

# import tkinter as tk
# from gui.main_window import MainWindow
# from gui.notification_window import NotificationWindow
# from watcher import DirectoryWatcher
# from config import load_config, save_config, add_directory, update_last_checked, get_last_checked

# def main():
#     root = tk.Tk()
#     root.title("File Watcher")

#     directories = load_config()

#     watcher = None

#     # Създаване на независим прозорец за нотификации
#     notification_window = NotificationWindow(master=root)

#     def start_watching():
#         nonlocal watcher
#         if watcher is None:
#             watcher = DirectoryWatcher(directories, notification_window.add_notification)
#             watcher.start_watching()

#     def stop_watching():
#         nonlocal watcher
#         if watcher is not None:
#             watcher.stop_watching()
#             watcher = None

#     def edit_directory(directory):
#         # Функция за редактиране на директория
#         save_config(directories)

#     def delete_directory(directory):
#         # Функция за изтриване на директория
#         directories.remove(directory)
#         save_config(directories)
#         app.update_directory_list(directories)

#     def add_directory_callback(new_directory):
#         # Функция за добавяне на нова директория
#         add_directory(directories, new_directory)
#         app.update_directory_list(directories)

#     # Основен прозорец - добавете липсващия аргумент 'notification_window'
#     app = MainWindow(root, directories, start_watching, stop_watching, edit_directory, delete_directory, add_directory_callback, notification_window)

#     # Показване на прозореца за нотификации
#     notification_window.show()

#     root.mainloop()

# if __name__ == "__main__":
#     main()

import tkinter as tk
from gui.main_window import MainWindow
from gui.notification_window import NotificationWindow
from watcher import DirectoryWatcher
from config import load_config, save_config, add_directory, update_last_checked, get_last_checked

def main():
    root = tk.Tk()
    root.title("File Watcher")

    directories = load_config()

    watcher = None

    # Създаване на независим прозорец за нотификации
    notification_window = NotificationWindow(master=root)

    def start_watching():
        nonlocal watcher
        if watcher is not None:  # Stop the existing watcher if it's running
            watcher.stop_watching()

        # Always create a new DirectoryWatcher instance
        watcher = DirectoryWatcher(directories, notification_window.add_notification)
        watcher.start_watching()

    def stop_watching():
        nonlocal watcher
        if watcher is not None:
            watcher.stop_watching()
            watcher = None

    def edit_directory(directory):
        # Функция за редактиране на директория
        save_config(directories)
        watcher.update_directories(directories)  # Уведомяване на DirectoryWatcher за промените

    def delete_directory(directory):
        # Функция за изтриване на директория
        directories.remove(directory)
        save_config(directories)
        watcher.remove_directory(directory['path'])  # Премахване от DirectoryWatcher
        app.update_directory_list(directories)

    def add_directory_callback(new_directory):
        # Функция за добавяне на нова директория
        add_directory(directories, new_directory)
        watcher.update_directories(directories)  # Уведомяване на DirectoryWatcher за промените
        app.update_directory_list(directories)

    # Основен прозорец - добавяме аргумента 'watcher'
    app = MainWindow(root, directories, start_watching, stop_watching, edit_directory, delete_directory, add_directory_callback, notification_window, watcher)

    # Показване на прозореца за нотификации
    notification_window.show()

    root.mainloop()

if __name__ == "__main__":
    main()