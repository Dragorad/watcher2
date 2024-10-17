import os
import json
import time
import logging
import logging.handlers
import queue
from datetime import datetime, date, timedelta
import sched
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from plyer import notification
from config import update_last_checked
from pushbullet import Pushbullet
from dotenv import load_dotenv
# from firebase_admin import credentials, messaging, initialize_app


load_dotenv()
api_token = os.getenv("PUSHBULLET_API_TOKEN")
# firebase_credentiaals_json = os.getenv("FIREBASE_CREDENTIALS")
# cred = credentials.Certificate("filewatcher-dragorad-firebase.json")

print(api_token)
# print(firebase_credentiaals_json.project_id)
# initialize_app(cred)

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
        logging.shutdown()

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
           
            return True

    def send_notifications(self, title, message):
            log_notification(title, message)
            push = pb.push_note(title,message)
            print("Pushbullet result", push)
            notification.notify(
                title = title,
                message = message,
                timeout = 5
            )

    def on_new_file(self, path, directory_path):
        logging.info(f"New file created at {path} in {directory_path}")
        update_last_checked(self.directories, directory_path)
        file_name = path.split('/')[-1]
        
        self.send_notifications(
            title= "new File Detected",
            message= f"New file created in {path}"
        )
        
        self.notification_callback('New file created ', directory_path , file_name)
        
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

        # Първо проверяваме дали днешният ден е сред дните за наблюдение
        if self.should_watch(directory):
            print(f"Today is a valid day for watching: {date.today().strftime('%A')}. Proceeding with time check.")
            
            # След това проверяваме дали текущото време е в рамките на start_time и end_time
            if start_time <= now.time() <= end_time:
                print(f"Current time is within the start and end time range for {directory['path']}.")
                self.start_observer(directory)
                self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))
            else:
                print(f"Current time is outside the start and end time range for {directory['path']}.")
                
                # Ако времето за стартиране е минало, планираме за утре
                if delay_to_start < 0:
                    delay_to_start += 24 * 60 * 60  # Планиране за следващия ден

                print(f"Scheduling start for {directory['path']} in {delay_to_start} seconds")
                print(f"Scheduling stop for {directory['path']} in {delay_to_stop} seconds")

                self.scheduler.enter(delay_to_start, 1, self.start_observer, argument=(directory,))
                self.scheduler.enter(delay_to_stop, 1, self.stop_observer, argument=(directory['path'],))
        else:
            print(f"Today is not a valid day for watching: {date.today().strftime('%A')}. Skipping observer start for {directory['path']}.")

    
    def start_observer(self, directory):
         
        print('start observer', self.observers)

        self.send_notifications(
            title="Observer Started",
            message=f"Observer started for {directory['path']}"
        )
        # notification.notify(
        #     title="Observer started",
        #     message=f"Observer started for {directory}",
        #     timeout=5
        # )
        self.notification_callback("Observer started",directory, "")
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
        # notification.notify(
        #     title="Observer Stopped",
        #     message=f"Observer stopped for {path}",
        #     timeout=5
        # )
        self.send_notifications( 
            title="Observer Stopped",
            message=f"Observer stopped for {path}",)
        
        self.notification_callback("Obserfer Stopped", path, "")
        
        if path in self.observers:
            self.observers[path].stop()
            self.observers[path].join()
            del self.observers[path]
            logging.info(f"Observer stopped for: {path} at {datetime.now()}")