import tkinter as tk
from tkinter import filedialog
import json

config_file = "backup_config.json"

def save_config(directory, interval):
    config = {
        "directory": directory,
        "interval": interval
    }
    with open(config_file, "w") as f:
        json.dump(config, f)
    print("Configuration saved.")

def select_directory():
    directory = filedialog.askdirectory()
    folder_label.config(text=directory)
    return directory

def start_backup():
    directory = folder_label.cget("text")
    interval = interval_entry.get()
    save_config(directory, interval)

app = tk.Tk()
app.title("Automated File Backup System")

folder_button = tk.Button(app, text="Select Folder", command=select_directory)
folder_button.pack()
folder_label = tk.Label(app, text="No folder selected")
folder_label.pack()

interval_label = tk.Label(app, text="Backup Interval (hours):")
interval_label.pack()
interval_entry = tk.Entry(app)
interval_entry.pack()

start_button = tk.Button(app, text="Save Configuration", command=start_backup)
start_button.pack()

app.mainloop()
