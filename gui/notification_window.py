import tkinter as tk
from tkinter import ttk
from datetime import datetime

class NotificationWindow:
    def __init__(self, master=None):
        # Създаване на нов независим прозорец за нотификации
        self.window = tk.Toplevel(master)
        self.window.title("Notifications")
        
        # Настройване на фиксиран размер на прозореца (800x600 пиксела)
        window_width = 840
        window_height = 600
        self.window.geometry(f"{window_width}x{window_height}")

        # Позициониране на прозореца в най-дясната част на екрана с отместване от 100 пиксела
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = screen_width - window_width - 100  # Отместване с 100 пиксела от десния ръб
        y_position = (screen_height - window_height) // 2  # Центриране по вертикала
        self.window.geometry(f"+{x_position}+{y_position}")

        # Създаване на външна рамка за съдържанието с канвас за скролиране
        self.outer_frame = tk.Frame(self.window)
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.outer_frame, width=window_width)
        self.scrollbar_y = ttk.Scrollbar(self.outer_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.outer_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, width=window_width)

        # Свързване на Scrollbar към канваса
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Поставяне на скролбара отляво и съдържанието отдясно
        self.scrollbar_y.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Секция за показване на текущия ден и дата
        self.current_date_label = tk.Label(self.scrollable_frame, text=self.get_current_day_date(), font=("Arial", 14))
        self.current_date_label.pack(pady=5, fill=tk.X)
        
        # Създаване на секция за Running Observers с намалена височина и скролбар
        self.running_label = tk.Label(self.scrollable_frame, text="Running Observers", bg="#e0f7fa", font=("Arial", 12, "bold"))
        self.running_label.pack(fill=tk.X, pady=(10, 0))

        running_frame = tk.Frame(self.scrollable_frame)
        running_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        self.running_tree = ttk.Treeview(running_frame, columns=("directory", "end_time"), show="headings", height=3)
        self.running_tree.heading("directory", text="Directory")
        self.running_tree.heading("end_time", text="End Time")
        self.running_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        running_scrollbar = ttk.Scrollbar(running_frame, orient="vertical", command=self.running_tree.yview)
        self.running_tree.configure(yscroll=running_scrollbar.set)
        running_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Създаване на секция за Scheduled Observers с намалена височина и скролбар
        self.scheduled_label = tk.Label(self.scrollable_frame, text="Scheduled Observers", bg="#ffecb3", font=("Arial", 12, "bold"))
        self.scheduled_label.pack(fill=tk.X, pady=(10, 0))

        scheduled_frame = tk.Frame(self.scrollable_frame)
        scheduled_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        self.scheduled_tree = ttk.Treeview(scheduled_frame, columns=("directory", "start_time"), show="headings", height=3)
        self.scheduled_tree.heading("directory", text="Directory")
        self.scheduled_tree.heading("start_time", text="Start Time")
        self.scheduled_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scheduled_scrollbar = ttk.Scrollbar(scheduled_frame, orient="vertical", command=self.scheduled_tree.yview)
        self.scheduled_tree.configure(yscroll=scheduled_scrollbar.set)
        scheduled_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Създаване на Treeview за текущи нотификации с добавен Scrollbar
        notifications_frame = tk.Frame(self.scrollable_frame)
        notifications_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(notifications_frame, columns=("time", "action", "directory", "file"), show="headings", height=10)
        self.tree.heading("time", text="Time")
        self.tree.heading("action", text="Action")
        self.tree.heading("directory", text="Directory")
        self.tree.heading("file", text="File Name")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Добавяне на Scrollbar към секцията с нотификации
        notification_scrollbar = ttk.Scrollbar(notifications_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=notification_scrollbar.set)
        notification_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Създаване на рамка за бутоните, за да ги поставим на един ред
        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Добавяне на бутон за изчистване на текущите нотификации
        clear_notifications_button = tk.Button(button_frame, text="Clear Current Notifications", command=self.clear_current_notifications)
        clear_notifications_button.pack(side=tk.LEFT, padx=5)

        # Добавяне на бутон за изчистване на лог файла
        clear_log_button = tk.Button(button_frame, text="Clear Notification Log", command=self.clear_notifications_log)
        clear_log_button.pack(side=tk.LEFT, padx=5)

        # Добавяне на бутон за затваряне на прозореца
        close_button = tk.Button(button_frame, text="Close", command=self.hide)
        close_button.pack(side=tk.LEFT, padx=5)

        # Правим така, че прозорецът да се крие вместо да се затваря
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

    def get_current_day_date(self):
        # Връща текущия ден от седмицата и дата като текст
        today = datetime.now().strftime('%A, %Y-%m-%d')
        return f"Today is: {today}"

    def add_running_observer(self, directory, end_time):
        # Добавяне на текущо работещ обзървър в таблицата
        self.running_tree.insert("", tk.END, values=(directory, end_time))

    def remove_running_observer(self, directory):
        # Премахване на обзървър от таблицата на текущо работещи
        for item in self.running_tree.get_children():
            if self.running_tree.item(item)['values'][0] == directory:
                self.running_tree.delete(item)

    def add_scheduled_observer(self, directory, start_time):
        # Добавяне на планиран обзървър в таблицата
        self.scheduled_tree.insert("", tk.END, values=(directory, start_time))

    def add_notification(self, message_action, message_directory, message_filename):
        # Добавяне на нотификацията в прозореца с текущото време
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tree.insert("", tk.END, values=(time_str, message_action, message_directory, message_filename))

    def clear_current_notifications(self):
        # Премахване на всички елементи от Treeview (изчистване на визуализираните нотификации)
        for item in self.tree.get_children():
            self.tree.delete(item)
        print("Current notifications cleared.")

    def clear_notifications_log(self):
        # Изтриване на съдържанието на файла notifications.log
        open('notifications.log', 'w').close()
        print("Notification log cleared.")

    def show(self):
        # Показване на прозореца за нотификации
        self.window.deiconify()
        self.window.lift()
        self.window.attributes('-topmost', True)  # Дръж прозореца винаги отгоре

    def hide(self):
        # Скриване на прозореца за нотификации
        self.window.withdraw()
