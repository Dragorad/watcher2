
# import os
# import time
# import logging
# from datetime import datetime
# from watchdog.observers.polling import PollingObserver
# from watchdog.events import FileSystemEventHandler
# from plyer import notification
# from config import update_last_checked, get_last_checked

# LOG_FILE = 'watcher.log'
# logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# class WatcherHandler(FileSystemEventHandler):
#     def __init__(self, callback):
#         self.callback = callback

#     def on_created(self, event):
#         if not event.is_directory:
#             logging.info(f"New file detected: {event.src_path}")
#             self.callback(event.src_path)

# class DirectoryWatcher:
#     def __init__(self, directories, notification_callback):
#         self.directories = directories
#         self.notification_callback = notification_callback
#         self.observers = {} 
#         self.running = False

#     def start_watching(self):
#         if self.running:
#             return
#         self.running = True

#         for directory in self.directories:
#             if self.should_watch(directory): 
#                 handler = WatcherHandler(lambda path: self.on_new_file(path, directory['path']))
#                 observer = PollingObserver(timeout=directory.get('interval', 1)) 
#                 observer.schedule(handler, directory['path'], recursive=True)
#                 self.observers[directory['path']] = observer 
#                 observer.start()

#     def stop_watching(self):
#         if not self.running:
#             return
#         for observer in self.observers.values():
#             observer.stop()
#             observer.join()
#         self.observers = {} 
#         self.running = False

#     def should_watch(self, directory):
#         now = datetime.now().time()
#         start_time = datetime.strptime(directory['start_time'], '%H:%M').time()
#         end_time = datetime.strptime(directory['end_time'], '%H:%M').time()
#         return start_time <= now <= end_time

#     def on_new_file(self, path, directory_path):
#         logging.info(f"New file created at {path} in {directory_path}")
#         update_last_checked(self.directories, directory_path)

#         notification.notify(
#             title="New File Detected",
#             message=f"New file created at {path} in {directory_path}",
#             timeout=5
#         )

#         self.notification_callback(f"New file created at {path} in {directory_path}")

import os
import time
import logging
from datetime import datetime
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from plyer import notification
from config import update_last_checked

LOG_FILE = 'watcher.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            self.callback(event.src_path)

class DirectoryWatcher:
    def __init__(self, directories, notification_callback):
        self.directories = directories
        self.notification_callback = notification_callback
        self.observers = {} 
        self.running = False

    def start_watching(self):
        if self.running:
            return
        self.running = True

        for directory in self.directories:
            if self.should_watch(directory): 
                handler = WatcherHandler(lambda path: self.on_new_file(path, directory['path']))
                # Използваме 'interval' за timeout на PollingObserver
                observer = PollingObserver(timeout=directory.get('interval', 5))  
                observer.schedule(handler, directory['path'], recursive=True)
                self.observers[directory['path']] = observer 
                observer.start()

    def stop_watching(self):
        if not self.running:
            return
        for observer in self.observers.values():
            observer.stop()
            observer.join()
        self.observers = {} 
        self.running = False

    def should_watch(self, directory):
        now = datetime.now().time()
        start_time = datetime.strptime(directory['start_time'], '%H:%M').time()
        end_time = datetime.strptime(directory['end_time'], '%H:%M').time()
        return start_time <= now <= end_time

    def on_new_file(self, path, directory_path):
        logging.info(f"New file created at {path} in {directory_path}")
        update_last_checked(self.directories, directory_path)

        notification.notify(
            title="New File Detected",
            message=f"New file created at {path} in {directory_path}",
            timeout=5
        )

        self.notification_callback(f"New file created at {path} in {directory_path}")

    def update_directories(self, new_directories):
        """Актуализира списъка с наблюдавани директории."""
        self.stop_watching() 
        self.directories = new_directories
        self.start_watching() 

    def remove_directory(self, path):
        """Премахва директория от наблюдение."""
        if path in self.observers:
            self.observers[path].stop()
            self.observers[path].join()
            del self.observers[path]
        self.directories = [d for d in self.directories if d['path'] != path]