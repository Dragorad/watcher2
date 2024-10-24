  
import os
import json
import time
import logging
import logging.handlers
import queue
from datetime import datetime, date, timedelta, time as dt_time
import sched
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from plyer import notification
from config import update_last_checked
from pushbullet import Pushbullet
from dotenv import load_dotenv

load_dotenv()
api_token = os.getenv("PUSHBULLET_API_TOKEN")
pb = Pushbullet(api_token)

notification_log_queue = queue.Queue()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
notification_file_handler = logging.FileHandler('notifications.log')
notification_file_handler.setFormatter(formatter)
notification_queue_handler = logging.handlers.QueueHandler(notification_log_queue)
notification_logger = logging.getLogger('notification_logger')
notification_logger.setLevel(logging.INFO)
notification_logger.addHandler(notification_queue_handler)
notification_queue_listener = logging.handlers.QueueListener(notification_log_queue, notification_file_handler)
notification_queue_listener.start()

# Функция за логване на нотификацията
def log_notification(title, message):
    notification_logger.info(f"Notification - Title: {title}, Message: {message}")

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            self.callback(event.src_path)

class DirectoryWatcher:
    def __init__(self, directories, notification_window):
        self.directories = directories
        self.notification_callback = notification_window.add_notification
        self.observers = {} 
        self.running = False
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.notification_window = notification_window

    def send_notifications(self, title, message):
        log_notification(title, message)
        push = pb.push_note(title, message)
        print("Pushbullet result", push)
        notification.notify(title=title, message=message, timeout=5)

    def start_watching(self):
        logging.info("Методът start_watching е извикан") 
        if self.running:
            return
        self.running = True

        # Планираме проверка на деня от седмицата всеки ден в 11:00 часа.
        self.schedule_daily_check()

        # Планираме наблюдението за всяка директория
        for directory in self.directories:
            self.schedule_monitoring(directory)

        # Стартиране на планировчика в отделна нишка
        threading.Thread(target=self.scheduler.run).start()
        print('threading start')

    def stop_watching(self):
        if not self.running:
            return

        for path, observer in self.observers.items():
            observer.stop()
            observer.join()
            logging.info(f"Спряно наблюдение на директория: {path}")

        self.observers = {} 
        self.running = False
        logging.shutdown()

        # Изчистване на планировчика
        for event in self.scheduler.queue:
            self.scheduler.cancel(event)

    def should_watch(self, directory):
        today = date.today().weekday() 
        days_to_watch = directory['days']
        weekdays = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"]
        today_str = weekdays[today]
        return days_to_watch and today_str in days_to_watch

    def schedule_daily_check(self):
        """
        Планира ежедневна проверка на деня от седмицата в 11:00 часа.
        """
        now = datetime.now()
        daily_check_time = datetime.combine(now.date(), dt_time(11, 0))
        
        if now.time() > daily_check_time.time():
            # Ако времето за проверка вече е минало за днешния ден, планираме за утре.
            daily_check_time += timedelta(days=1)
        
        delay_to_daily_check = (daily_check_time - now).total_seconds()

        # Планиране на проверката за следващия ден
        self.scheduler.enter(delay_to_daily_check, 1, self.daily_check)

    def daily_check(self):
        """
        Проверява дали текущият ден е сред дните за наблюдение и създава задачи за стартиране на наблюдатели.
        """
        print(f"Daily check executed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for directory in self.directories:
            if self.should_watch(directory):
                self.schedule_monitoring(directory)
        
        # Планира отново проверка за следващия ден в 11:00 часа.
        self.schedule_daily_check()

    def on_new_file(self, path, directory_path):
        logging.info(f"New file created at {path} in {directory_path}")
        update_last_checked(self.directories, directory_path)
        file_name = path.split('/')[-1]
        
        self.send_notifications(
            title="New File Detected",
            message=f"New file created in {path}"
        )
        
        self.notification_callback('New file created', directory_path, file_name)
        
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
        logging.info(f"Директорията {path} е премахната от конфигурацията")
    
    def start_observer(self, directory):
        print('start observer', self.observers)
        self.send_notifications(
            title="Observer Started",
            message=f"Observer started for {directory['path']}"
        )
        self.notification_callback("Observer started", directory, "")
        if directory['path'] not in self.observers:
            try:
                handler = WatcherHandler(lambda path: self.on_new_file(path, directory['path']))
                observer = PollingObserver(timeout=directory.get('interval', 1))
                observer.schedule(handler, directory['path'], recursive=True)
                self.observers[directory['path']] = observer
                observer.start()
                
                end_time = datetime.combine(datetime.now().date(), datetime.strptime(directory['end_time'], '%H:%M').time())
                self.notification_window.add_running_observer(directory['path'], end_time.strftime('%Y-%m-%d %H:%M:%S'))

            except Exception as e:
                logging.error(f"Error starting observer for {directory['path']}: {e}")
                self.send_notifications(f"Problem starting observer for {directory['path']}")

    def stop_observer(self, path):
        print('Observer stopped', path)
        self.send_notifications(
            title="Observer Stopped",
            message=f"Observer stopped for {path}"
        )
        self.notification_callback("Observer Stopped", path, "")
        
        if path in self.observers:
            self.observers[path].stop()
            self.observers[path].join()
            del self.observers[path]
            self.notification_window.remove_running_observer(path)
            logging.info(f"Observer stopped for: {path} at {datetime.now()}")

        # След като спрем наблюдателя, планираме неговото рестартиране на следващия ден
        for directory in self.directories:
            if directory['path'] == path:
                self.schedule_next_day(directory)

    def schedule_next_day(self, directory):
        """
        Планира стартиране на наблюдателя на следващия ден в start_time.
        """
        now = datetime.now()
        next_day = now + timedelta(days=1)
        start_time = datetime.strptime(directory['start_time'], '%H:%M').time()
        start_datetime = datetime.combine(next_day.date(), start_time)
        delay_to_start = (start_datetime - now).total_seconds()

        # Актуализиране на секцията за планирани наблюдатели в прозореца с нотификации
        self.notification_window.add_scheduled_observer(directory['path'], start_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        
        self.scheduler.enter(delay_to_start, 1, self.start_observer, argument=(directory,))
        print(f"Scheduled start for {directory['path']} on next day at {start_datetime}")

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

        if self.should_watch(directory):
            if start_time <= now.time() <= end_time:
                self.start_observer(directory)
                if delay_to_stop < 0:
                    delay_to_stop += 24 * 60 * 60
                self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))
            else:
                if delay_to_start < 0:
                    delay_to_start += 24 * 60 * 60
                self.scheduler.enter(delay_to_start, 1, self.start_observer, argument=(directory,))
                self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))
                # Добавяне на планирания наблюдател в секцията за планирани
                self.notification_window.add_scheduled_observer(directory['path'], start_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print(f"Today is not a valid day for watching: {date.today().strftime('%A')}.")
