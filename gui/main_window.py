import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui.crud_modal import CrudModal

class MainWindow(tk.Frame):
    def __init__(self, root, directories, start_callback, stop_callback, edit_callback, delete_callback, add_callback, notification_window, watcher):
        super().__init__(root)
        self.root = root
        self.directories = directories
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.add_callback = add_callback
        self.notification_window = notification_window
        self.watcher = watcher

        self.is_watching = False

        self.setup_ui()

    def set_watcher(self, watcher):
        """
        Задава нова инстанция на DirectoryWatcher.
        """
        self.watcher = watcher

    def setup_ui(self):
               
        self.pack(fill=tk.BOTH, expand=True)

        # Frame за основните бутони
        self.main_buttons_frame = tk.Frame(self)
        self.main_buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Start/Stop Watching Button
        self.watch_button = tk.Button(self.main_buttons_frame, text="Start Watching", command=self.toggle_watching)
        self.watch_button.pack(side=tk.LEFT, padx=5)

        # Add Directory Button
        self.add_button = tk.Button(self.main_buttons_frame, text="Add Directory", command=self.open_add_directory_modal)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Show Notification Window Button
        self.show_notifications_button = tk.Button(self.main_buttons_frame, text="Show Notifications", command=self.notification_window.show)
        self.show_notifications_button.pack(side=tk.LEFT, padx=5)

        # Treeview за показване на директориите
        style = ttk.Style()
        style.configure("Directory.Column", weight=12, parent="Treeview.Column")
        style.configure("Days.Column", weight=10, parent="Treeview.Column")
        style.configure("Time.Column", weight=1, parent="Treeview.Column")
        style.configure("Actions.Column", weight=2, parent="Treeview.Column")

        self.directory_tree = ttk.Treeview(self, columns=("Path", "Days", "Start Time", "End Time", "Interval", "Edit", "Delete"), show="headings")
        
       
        self.directory_tree.columnconfigure(0, weight=12,minsize=350)  # Path
        self.directory_tree.columnconfigure(1, weight=12, minsize=350)  # Days
        self.directory_tree.columnconfigure(2, weight=1,)  # Start Time
        self.directory_tree.columnconfigure(3, weight=1)  # End Time
        self.directory_tree.columnconfigure(4, weight=1, minsize=20)  # Interval
        self.directory_tree.columnconfigure(5, weight=2, minsize=30)  # Edit
        self.directory_tree.columnconfigure(6, weight=2,minsize=30)  # Delete

        self.directory_tree.heading("Path", text="Path")
        self.directory_tree.heading("Days", text="Days")
        self.directory_tree.heading("Start Time", text="Start Time")
        self.directory_tree.heading("End Time", text="End Time")
        self.directory_tree.heading("Interval", text="Interval (min)")
        self.directory_tree.heading("Edit", text="Edit")
        self.directory_tree.heading("Delete", text="Delete")

        self.directory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.update_directory_list(self.directories)

    def update_directory_list(self, directories):
        """Обновява списъка с директории на интерфейса."""

        existing_items = set(self.directory_tree.get_children())
        new_items = {(d['path'], ", ".join(d['days']), d['start_time'], d['end_time'], str(d['interval'] // 60)) for d in directories}

        # Актуализиране или изтриване на съществуващи елементи
        for item in existing_items:
            values = self.directory_tree.item(item)['values']
            if tuple(values[:-2]) in new_items:
                new_items.remove(tuple(values[:-2]))
                # Актуализираме стойностите, ако са променени
                for i, new_value in enumerate(new_items):
                    if values[i] != new_value:
                        self.directory_tree.item(item, values=(
                            *values[:-2], "Edit", "Delete"
                        ))
                        break
            else:
                self.directory_tree.delete(item)

        # Добавяне на нови елементи
        for path, days, start_time, end_time, interval in new_items:
            self.directory_tree.insert("", "end", values=(
                path, days, start_time, end_time, interval, "Edit", "Delete"
            ))

        # Свързване на избор на дърво
        self.directory_tree.bind("<Double-1>", self.on_tree_item_double_click)

    def on_tree_item_double_click(self, event):
        """Handler за двоен клик върху елемент от дървото за действия за редактиране/изтриване."""
        selected_item = self.directory_tree.selection()
        if selected_item:
            item = self.directory_tree.item(selected_item)
            item_values = item['values']
            path = item_values[0]

            # Определяне дали е необходимо действие за редактиране или изтриване въз основа на колоната
            column = self.directory_tree.identify_column(event.x)
            if column == "#6":  # Колона Edit
                directory = next((d for d in self.directories if d['path'] == path), None)
                if directory:
                    self.open_edit_directory_modal(directory)
            elif column == "#7":  # Колона Delete
                self.delete_directory(path)

    def delete_directory(self, path):
        """Функция за изтриване на директория по пътя."""
        result = messagebox.askyesno("Delete Directory", f"Are you sure you want to delete the directory '{path}'?")
        if result:
            # Remove the directory from the list
            self.directories = [d for d in self.directories if d['path'] != path]
            # Remove from DirectoryWatcher
            self.watcher.remove_directory(path)
            self.update_directory_list(self.directories)
            self.delete_callback(path)  # уведомяваме app.py

    def open_add_directory_modal(self):
        """Отваря модален прозорец за добавяне на нова директория."""
        CrudModal(self.root, self.directories, self.handle_add_directory, self.edit_callback, self.delete_callback)

    def open_edit_directory_modal(self, directory):
        """Отваря модален прозорец за редактиране на съществуваща директория."""
        CrudModal(self.root, self.directories, self.handle_edit_directory, self.edit_callback, self.delete_callback, directory)

    def handle_add_directory(self, path, days, start_time, end_time, interval, _):
        """Обработва добавянето на нова директория."""
        new_directory = {
            'path': path,
            'days': days,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval
        }
        self.directories.append(new_directory)
        self.add_callback(new_directory)
        self.watcher.update_directories(self.directories)
        self.update_directory_list(self.directories)

    
    def handle_edit_directory(self, path, days, start_time, end_time, interval, directory):
        """Обработва редактирането на съществуваща директория."""
        directory.update({
            'path': path,
            'days': days,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval
        })
        self.edit_callback(directory)
        self.watcher.update_directories(self.directories)
        self.update_directory_list(self.directories)

    def update_button_state(self, text, color):
        """Актуализира състоянието на бутона за наблюдение."""
        self.watch_button.config(text=text, bg=color)

    def toggle_watching(self):
        print(" MAIN TOGGLE W")
        """
        Превключва състоянието на наблюдение, като извиква метода от app.py
        """
        if self.is_watching:
            self.stop_callback()
        else:
            self.start_callback()
        
        # Актуализираме състоянието на бутона след като app.py е обработил заявката
        self.is_watching = not self.is_watching
        if self.is_watching:
            self.watch_button.config(text="Stop Watching", bg="green")
        else:
            self.watch_button.config(text="Start Watching", bg="SystemButtonFace")

    def start_watching(self):
        """Dummy method to avoid errors if called directly."""
        pass

    def stop_watching(self):
        """Dummy method to avoid errors if called directly."""
        pass