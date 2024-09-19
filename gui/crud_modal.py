import tkinter as tk

class CrudModal:
    def __init__(self, root, directories, on_confirm, edit_callback, delete_callback, directory=None):
        self.root = root
        self.directories = directories
        self.on_confirm = on_confirm
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.directory = directory

        self.modal = tk.Toplevel(self.root)
        self.modal.title("Add/Edit Directory")

        self.setup_ui()
        self.populate_fields()

    def setup_ui(self):
        tk.Label(self.modal, text="Path:").grid(row=0, column=0, padx=5, pady=5)
        self.path_entry = tk.Entry(self.modal, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.modal, text="Days:").grid(row=1, column=0, padx=5, pady=5)
        self.days_entry = tk.Entry(self.modal, width=50)
        self.days_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.modal, text="Start Time:").grid(row=2, column=0, padx=5, pady=5)
        self.start_time_entry = tk.Entry(self.modal, width=50)
        self.start_time_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.modal, text="End Time:").grid(row=3, column=0, padx=5, pady=5)
        self.end_time_entry = tk.Entry(self.modal, width=50)
        self.end_time_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.modal, text="Interval (min):").grid(row=4, column=0, padx=5, pady=5)
        self.interval_entry = tk.Entry(self.modal, width=50)
        self.interval_entry.grid(row=4, column=1, padx=5, pady=5)

        confirm_button = tk.Button(self.modal, text="Confirm", command=self.handle_confirm)
        confirm_button.grid(row=5, columnspan=2, pady=10)

        if self.directory:  # Ако редактираме, добавяме бутон за изтриване
            delete_button = tk.Button(self.modal, text="Delete", command=self.handle_delete)
            delete_button.grid(row=6, columnspan=2, pady=5)

    def populate_fields(self):
        if self.directory:
            self.path_entry.insert(0, self.directory['path'])
            self.days_entry.insert(0, ", ".join(self.directory['days']))
            self.start_time_entry.insert(0, self.directory['start_time'])
            self.end_time_entry.insert(0, self.directory['end_time'])
            self.interval_entry.insert(0, str(self.directory['interval'] // 60))

    def handle_confirm(self):
        path = self.path_entry.get()
        days = self.days_entry.get().split(", ")
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()
        interval = int(self.interval_entry.get()) * 60

        self.on_confirm(path, days, start_time, end_time, interval, self.directory)

        self.modal.destroy()

    def handle_delete(self):
        """
        Обработва изтриването на директория.
        """
        result = messagebox.askyesno("Delete Directory", f"Are you sure you want to delete the directory '{self.directory['path']}'?")
        if result:
            self.delete_callback(self.directory)
            self.modal.destroy()