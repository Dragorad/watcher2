import tkinter as tk
import logging 

# Import from the 'gui' package
from gui.main_window import MainWindow
from gui.notification_window import NotificationWindow

from watcher import DirectoryWatcher
from config import load_config, save_config, add_directory

# Конфигуриране на logging за app.py
print('bevore logging config')
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Entering main function")
    print('Entering in main')
    root = tk.Tk()
    root.geometry("800x300+100+100")
    root.title("File Watcher")

    directories = load_config()
    logging.info(f"Directories loaded from config: {directories}")

    global watcher 
    watcher = None

    # Създаване на независим прозорец за нотификации
    notification_window = NotificationWindow(master=root)

    def start_watching():
        global watcher
        print(" APP START")
        logging.info("Inside start_watching function")
        logging.info("Starting watching...") 
        logging.info(f"Watcher is None: {watcher is None}")
        if watcher is not None:
            watcher.stop_watching()

        watcher = DirectoryWatcher(directories, notification_window)
        watcher.start_watching()

        # Update the watcher reference in MainWindow
        app.set_watcher(watcher)

        app.update_button_state("Stop Watching", "green")  # Актуализиране на бутона в GUI
        logging.info("Watching started successfully")

    def stop_watching():
        global watcher
        logging.info("Stopping watching...")
        if watcher is not None:
            watcher.stop_watching()
            watcher = None
            app.update_button_state("Start Watching", "SystemButtonFace")
            logging.info("Watching stopped successfully")

    def toggle_watching():
        """Превключва състоянието на наблюдение."""
        if app.is_watching:
            stop_watching()
        else:
            start_watching()

    def edit_directory(directory):
        """Функция за редактиране на директория."""
        save_config(directories)
        if watcher is not None: 
            watcher.update_directories(directories)
        app.update_directory_list(directories)

    def delete_directory(directory):
        """Функция за изтриване на директория."""
        directories.remove(directory)
        save_config(directories)
        if watcher is not None:
            watcher.remove_directory(directory['path'])
        app.update_directory_list(directories)

    def add_directory_callback(new_directory):
        """Функция за добавяне на нова директория."""
        add_directory(directories, new_directory)
        if watcher is not None:
            watcher.update_directories(directories)
        app.update_directory_list(directories)

    # Основен прозорец -  предаваме None за watcher първоначално
    app = MainWindow(
        root, directories, start_watching, stop_watching, 
        edit_directory, delete_directory, add_directory_callback, 
        notification_window, None  # Pass None for watcher initially
    )

    # Показване на прозореца за нотификации
    notification_window.show()

    root.mainloop()

if __name__ == "__main__":
    main()