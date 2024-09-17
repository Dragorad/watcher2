
# import tkinter as tk
# from tkinter import ttk
# from tkinter import messagebox

# class MainWindow(tk.Frame):
#     def __init__(self, root, directories, start_callback, stop_callback, edit_callback, delete_callback, add_callback, notification_window):
#         super().__init__(root)
#         self.root = root
#         self.directories = directories
#         self.start_callback = start_callback
#         self.stop_callback = stop_callback
#         self.edit_callback = edit_callback
#         self.delete_callback = delete_callback
#         self.add_callback = add_callback
#         self.notification_window = notification_window

#         self.is_watching = False  

#         self.setup_ui()
#         self.start_watching()  # Автоматично стартиране на наблюдението при стартиране на приложението

#     def setup_ui(self):
#         self.pack(fill=tk.BOTH, expand=True)

#         # Frame за основните бутони
#         self.main_buttons_frame = tk.Frame(self)
#         self.main_buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

#         # Start/Stop Watching Button
#         self.watch_button = tk.Button(self.main_buttons_frame, text="Start Watching", command=self.toggle_watching)
#         self.watch_button.pack(side=tk.LEFT, padx=5)

#         # Add Directory Button
#         self.add_button = tk.Button(self.main_buttons_frame, text="Add Directory", command=self.open_add_directory_modal)
#         self.add_button.pack(side=tk.LEFT, padx=5)

#         # Show Notification Window Button
#         self.show_notifications_button = tk.Button(self.main_buttons_frame, text="Show Notifications", command=self.notification_window.show)
#         self.show_notifications_button.pack(side=tk.LEFT, padx=5)

#         # Treeview за показване на директориите
#         self.directory_tree = ttk.Treeview(self, columns=("Path", "Days", "Start Time", "End Time", "Interval", "Edit", "Delete"), show="headings")
#         self.directory_tree.heading("Path", text="Path")
#         self.directory_tree.heading("Days", text="Days")
#         self.directory_tree.heading("Start Time", text="Start Time")
#         self.directory_tree.heading("End Time", text="End Time")
#         self.directory_tree.heading("Interval", text="Interval (min)")
#         self.directory_tree.heading("Edit", text="Edit")
#         self.directory_tree.heading("Delete", text="Delete")

#         self.directory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

#         self.update_directory_list(self.directories)

#     def update_directory_list(self, directories):
#         """Обновява списъка с директории на интерфейса."""
#         # Изчистване на текущите данни в дървото
#         for i in self.directory_tree.get_children():
#             self.directory_tree.delete(i)

#         for directory in directories:
#             # Добавяне на подробностите за директорията в дървото
#             self.directory_tree.insert("", "end", values=(
#                 directory['path'],
#                 ", ".join(directory['days']),
#                 directory['start_time'],
#                 directory['end_time'],
#                 str(directory['interval'] // 60),  # Преобразуване на секунди в минути
#                 "Edit",
#                 "Delete"
#             ))

#         # Свързване на избор на дърво
#         self.directory_tree.bind("<Double-1>", self.on_tree_item_double_click)

#     def on_tree_item_double_click(self, event):
#         """Handler за двоен клик върху елемент от дървото за действия за редактиране/изтриване."""
#         selected_item = self.directory_tree.selection()
#         if selected_item:
#             item = self.directory_tree.item(selected_item)
#             item_values = item['values']
#             path = item_values[0]

#             # Определяне дали е необходимо действие за редактиране или изтриване въз основа на колоната
#             column = self.directory_tree.identify_column(event.x)
#             if column == "#6":  # Колона Edit
#                 directory = next((d for d in self.directories if d['path'] == path), None)
#                 if directory:
#                     self.open_edit_directory_modal(directory)
#             elif column == "#7":  # Колона Delete
#                 self.delete_directory(path)

#     def delete_directory(self, path):
#         """Функция за изтриване на директория по пътя."""
#         result = messagebox.askyesno("Delete Directory", f"Are you sure you want to delete the directory '{path}'?")
#         if result:
#             # Намиране и премахване на директорията от списъка
#             self.directories = [d for d in self.directories if d['path'] != path]
#             self.update_directory_list(self.directories)
#             self.delete_callback(path)

#     def open_add_directory_modal(self):
#         """Отваря модален прозорец за добавяне на нова директория."""
#         self.open_directory_modal()

#     def open_edit_directory_modal(self, directory):
#         """Отваря модален прозорец за редактиране на съществуваща директория."""
#         self.open_directory_modal(directory)

#     def open_directory_modal(self, directory=None):
#         """
#         Отваря модален прозорец за добавяне или редактиране на директория.
#         :param directory: Съществуваща директория за редактиране. Ако е None, ще се добави нова.
#         """
#         modal = tk.Toplevel(self.root)
#         modal.title("Add/Edit Directory")

#         tk.Label(modal, text="Path:").grid(row=0, column=0, padx=5, pady=5)
#         path_entry = tk.Entry(modal, width=50)
#         path_entry.grid(row=0, column=1, padx=5, pady=5)

#         tk.Label(modal, text="Days:").grid(row=1, column=0, padx=5, pady=5)
#         days_entry = tk.Entry(modal, width=50)
#         days_entry.grid(row=1, column=1, padx=5, pady=5)

#         tk.Label(modal, text="Start Time:").grid(row=2, column=0, padx=5, pady=5)
#         start_time_entry = tk.Entry(modal, width=50)
#         start_time_entry.grid(row=2, column=1, padx=5, pady=5)

#         tk.Label(modal, text="End Time:").grid(row=3, column=0, padx=5, pady=5)
#         end_time_entry = tk.Entry(modal, width=50)
#         end_time_entry.grid(row=3, column=1, padx=5, pady=5)

#         tk.Label(modal, text="Interval (min):").grid(row=4, column=0, padx=5, pady=5)
#         interval_entry = tk.Entry(modal, width=50)
#         interval_entry.grid(row=4, column=1, padx=5, pady=5)

#         def on_confirm():
#             path = path_entry.get()
#             days = days_entry.get().split(", ")
#             start_time = start_time_entry.get()
#             end_time = end_time_entry.get()
#             interval = int(interval_entry.get()) * 60

#             if directory:
#                 # Update съществуваща директория
#                 directory.update({
#                     'path': path,
#                     'days': days,
#                     'start_time': start_time,
#                     'end_time': end_time,
#                     'interval': interval
#                 })
#                 self.edit_callback(directory)
#             else:
#                 # Добавяне на нова директория
#                 new_directory = {
#                     'path': path,
#                     'days': days,
#                     'start_time': start_time,
#                     'end_time': end_time,
#                     'interval': interval
#                 }
#                 self.directories.append(new_directory)
#                 self.add_callback(new_directory)

#             self.update_directory_list(self.directories)
#             modal.destroy()

#         # Попълване на текущите стойности при редактиране
#         if directory:
#             path_entry.insert(0, directory['path'])
#             days_entry.insert(0, ", ".join(directory['days']))
#             start_time_entry.insert(0, directory['start_time'])
#             end_time_entry.insert(0, directory['end_time'])
#             interval_entry.insert(0, str(directory['interval'] // 60))

#         confirm_button = tk.Button(modal, text="Confirm", command=on_confirm)
#         confirm_button.grid(row=5, columnspan=2, pady=10)

#     def start_watching(self):
#         """Стартира наблюдението на директориите."""
#         self.is_watching = True
#         self.watch_button.config(text="Stop Watching")
#         self.start_callback()

#     def stop_watching(self):
#         """Спира наблюдението на директориите."""
#         self.is_watching = False
#         self.watch_button.config(text="Start Watching")
#         self.stop_callback()

#     def toggle_watching(self):
#         """Превключва състоянието на наблюдение."""
#         if self.is_watching:
#             self.stop_watching()
#         else:
#             self.start_watching()

# # Вашият съществуващ код за старт на програмата

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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
     
    def toggle_watching(self):
        """Toggle watching state and update button text and color."""
        if self.is_watching:
            self.stop_watching()
        else:
            self.start_watching()

    def start_watching(self):
        """Start watching directories and update button."""
        self.is_watching = True
        self.watch_button.config(text="Stop Watching", bg="green") 
        self.start_callback()  # Call the provided callback function to start watching

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
        self.directory_tree = ttk.Treeview(self, columns=("Path", "Days", "Start Time", "End Time", "Interval", "Edit", "Delete"), show="headings")
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

    def open_add_directory_modal(self):
        """Отваря модален прозорец за добавяне на нова директория."""
        self.open_directory_modal()

    def open_edit_directory_modal(self, directory):
        """Отваря модален прозорец за редактиране на съществуваща директория."""
        self.open_directory_modal(directory)

    def open_directory_modal(self, directory=None):
        """
        Отваря модален прозорец за добавяне или редактиране на директория.
        :param directory: Съществуваща директория за редактиране. Ако е None, ще се добави нова.
        """
        modal = tk.Toplevel(self.root)
        modal.title("Add/Edit Directory")

        tk.Label(modal, text="Path:").grid(row=0, column=0, padx=5, pady=5)
        path_entry = tk.Entry(modal, width=50)
        path_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(modal, text="Days:").grid(row=1, column=0, padx=5, pady=5)
        days_entry = tk.Entry(modal, width=50)
        days_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(modal, text="Start Time:").grid(row=2, column=0, padx=5, pady=5)
        start_time_entry = tk.Entry(modal, width=50)
        start_time_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(modal, text="End Time:").grid(row=3, column=0, padx=5, pady=5)
        end_time_entry = tk.Entry(modal, width=50)
        end_time_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(modal, text="Interval (min):").grid(row=4, column=0, padx=5, pady=5)
        interval_entry = tk.Entry(modal, width=50)
        interval_entry.grid(row=4, column=1, padx=5, pady=5)

        def on_confirm():
            path = path_entry.get()
            days = days_entry.get().split(", ")
            start_time = start_time_entry.get()
            end_time = end_time_entry.get()
            interval = int(interval_entry.get()) * 60

            if directory:
                # Update existing directory
                directory.update({
                    'path': path,
                    'days': days,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval': interval  # Коригиран ред
                })
                self.edit_callback(directory)
                self.watcher.update_directories(self.directories)  # Notify DirectoryWatcher of changes
            else:
                # Adding new directory
                new_directory = {
                    'path': path,
                    'days': days,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval': interval
                }
                self.directories.append(new_directory)
                self.add_callback(new_directory)
                self.watcher.update_directories(self.directories)  # Notify DirectoryWatcher of changes

            self.update_directory_list(self.directories)
            modal.destroy()