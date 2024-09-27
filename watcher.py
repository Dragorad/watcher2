import os
import time
import logging
from datetime import datetime, date, timedelta
import sched
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from plyer import notification
from config import update_last_checked

# Конфигуриране на logging за watcher.py
logging.basicConfig(filename='watcher.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.scheduler = sched.scheduler(time.time, time.sleep) 
      
    def start_watching(self):
        
        logging.info("Методът start_watching е извикан") 
        if self.running:
            return
        self.running = True

        for directory in self.directories:
            self.schedule_monitoring(directory)

        # Стартиране на планировчика в отделна нишка
        threading.Thread(target=self.scheduler.run).start()
        print('treading start')

    def stop_watching(self):
        if not self.running:
            return

        for path, observer in self.observers.items():
            observer.stop()
            observer.join()
            logging.info(f"Спряно наблюдение на директория: {path}")

        self.observers = {} 
        self.running = False

        # Изчистване на планировчика
        for event in self.scheduler.queue:
            self.scheduler.cancel(event)

    def should_watch(self, directory):
        today = date.today().weekday() 
        
        days_to_watch = directory['days']

        weekdays = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"]
        today_str = weekdays[today]
        
        # Проверка дали текущият ден е в списъка с дни за наблюдение
        if days_to_watch and today_str not in days_to_watch:
            return False
        else:
            # now = datetime.now().time()
            # start_time = datetime.strptime(directory['start_time'], '%H:%M').time()
            # end_time = datetime.strptime(directory['end_time'], '%H:%M').time()
            # return start_time <= now <= end_time
            return True
        
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

    def schedule_monitoring(self, directory):
        """
        Планира стартирането и спирането на наблюдението на директория 
        въз основа на start_time и end_time.
        """
        now = datetime.now()
        start_time = datetime.strptime(directory['start_time'], '%H:%M').time()
        end_time = datetime.strptime(directory['end_time'], '%H:%M').time()


        start_datetime = datetime.combine(now.date(), start_time)
        end_datetime = datetime.combine(now.date(), end_time)

        if end_time < start_time:
            end_datetime += timedelta(days=1) 

        delay_to_start = (start_datetime - now).total_seconds()
        delay_to_stop = (end_datetime - now).total_seconds()

        if start_time <= now.time() <= end_time and self.should_watch(directory): 
            self.start_observer(directory) 
            self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))
        else:
            # Ако текущото време е извън интервала, планираме стартиране 
            # в началото на интервала и спиране в края му
            # delay_to_start = (datetime.combine(now.date(), start_time) - now).total_seconds()
            if delay_to_start < 0:  # Ако start_time е днес, но вече е минал, планираме за утре
                delay_to_start += 24 * 60 * 60 

            delay_to_stop = (datetime.combine(now.date(), end_time) - now).total_seconds()
            if delay_to_stop < 0:
                delay_to_stop += 24 * 60 * 60

            logging.info(f"Scheduling start for {directory['path']} in {delay_to_start} seconds")
            logging.info(f"Scheduling stop for {directory['path']} in {delay_to_stop} seconds")

            self.scheduler.enter(delay_to_start, 1, self.start_observer, argument=(directory,))
            self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))

    def start_observer(self, directory):
        
         
        print('start observer', self.observers)
        notification.notify(
            title="Observer started",
            message=f"Started observer for {directory}",
            timeout=5
        )
        self.notification_callback(f"Started observer for {directory}")
        """
        Стартира наблюдател за дадена директория.
        """
        if directory['path'] not in self.observers:
            try:
                handler = WatcherHandler(lambda path: self.on_new_file(path, directory['path']))
                observer = PollingObserver(timeout=directory.get('interval', 1))
                observer.schedule(handler, directory['path'], recursive=True)
                self.observers[directory['path']] = observer
                observer.start()
                logging.info(f"Observer started for: {directory['path']} at {datetime.now()}")
            except Exception as e:
                logging.error(f"Error starting observer for {directory['path']}: {e}")

    def stop_observer(self, path):
        """
        Спира наблюдател за дадена директория.
        """
        print('stop observer', self.observers)
        notification.notify(
            title="Observer Stopped",
            message=f"Started observer for {path}",
            timeout=5
        )
        self.notification_callback(f"Stopped observer for {path}")
        
        if path in self.observers:
            self.observers[path].stop()
            self.observers[path].join()
            del self.observers[path]
            logging.info(f"Observer stopped for: {path} at {datetime.now()}")