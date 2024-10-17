import tkinter as tk
from tkinter import ttk
from datetime import datetime

class NotificationWindow:
    def __init__(self, master=None):
        # Създаване на нов независим прозорец за нотификации
        self.window = tk.Toplevel(master)
        self.window.title("Notifications")
        
        # Това прави прозореца винаги отгоре (но това е по избор)
        self.window.attributes('-topmost', False)

         # Секция за показване на текущия ден и дата
        self.current_date_label = tk.Label(self.window, text=self.get_current_day_date(), font=("Arial", 14))
        self.current_date_label.pack(pady=5)
        
        # Създаване на секция за Running Observers
        self.running_label = tk.Label(self.window, text="Running Observers", bg="#e0f7fa", font=("Arial", 12, "bold"))
        self.running_label.pack(fill=tk.X, pady=(10, 0))

        self.running_tree = ttk.Treeview(self.window, columns=("directory", "end_time"), show="headings")
        self.running_tree.heading("directory", text="Directory")
        self.running_tree.heading("end_time", text="End Time")
        self.running_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Създаване на секция за Scheduled Observers
        self.scheduled_label = tk.Label(self.window, text="Scheduled Observers", bg="#ffecb3", font=("Arial", 12, "bold"))
        self.scheduled_label.pack(fill=tk.X, pady=(10, 0))

        self.scheduled_tree = ttk.Treeview(self.window, columns=("directory", "start_time"), show="headings")
        self.scheduled_tree.heading("directory", text="Directory")
        self.scheduled_tree.heading("start_time", text="Start Time")
        self.scheduled_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        
        self.tree = ttk.Treeview(self.window, columns=("time","action", "directory", "file"), show="headings")
        self.tree.heading("time", text="Time")
        self.tree.heading("action", text="Action")
        self.tree.heading("directory", text="Directory")
        self.tree.heading("file", text="File Name")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавяне на Scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Добавяне на бутон за изчистване на текущите нотификации
        clear_notifications_button = tk.Button(self.window, text="Clear Current Notifications", command=self.clear_current_notifications)
        clear_notifications_button.pack(pady=5)

        # Добавяне на бутон за изчистване на лог файла
        clear_log_button = tk.Button(self.window, text="Clear Notification Log", command=self.clear_notifications_log)
        clear_log_button.pack(pady=5)


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
