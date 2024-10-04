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

        # Правим така, че прозорецът да се крие вместо да се затваря
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

    def add_notification(self, message_action, message_directory, message_filename):
        # Добавяне на нотификацията в прозореца с текущото време
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tree.insert("", tk.END, values=(time_str, message_action, message_directory, message_filename))

    def show(self):
        # Показване на прозореца за нотификации
        self.window.deiconify()
        self.window.lift()
        self.window.attributes('-topmost', True)  # Дръж прозореца винаги отгоре

    def hide(self):
        # Скриване на прозореца за нотификации
        self.window.withdraw()
