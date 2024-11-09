import tkinter as tk
from tkinter import filedialog, messagebox
import json
import boto3
import threading
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# AWS S3 configuration
aws_access_key = ''
aws_secret_key = ''
bucket_name = ''

config_file = "backup_config.json"

def save_config(directory, interval, email_notifications):
    config = {
        "directory": directory,
        "interval": interval,
        "email_notifications": email_notifications
    }
    with open(config_file, "w") as f:
        json.dump(config, f)
    print("Configuration saved.")

def select_directory():
    directory = filedialog.askdirectory()
    folder_label.config(text=directory)
    return directory

def validate_directory(directory):
    if not os.path.exists(directory):
        messagebox.showerror("Error", "The selected folder does not exist.")
        return False
    return True

def start_backup():
    directory = folder_label.cget("text")
    interval = interval_entry.get()
    email_notifications = email_var.get()  # Check if email notifications are enabled
    
    if not directory:
        messagebox.showerror("Error", "Please select a folder.")
        return
    if not interval.isdigit() or int(interval) <= 0:
        messagebox.showerror("Error", "Interval must be a positive number greater than 0.")
        return
    if not validate_directory(directory):
        return

    save_config(directory, interval, email_notifications)
    
    # Start the backup thread
    backup_thread = threading.Thread(target=automate_backup, args=(directory, int(interval), email_notifications))
    backup_thread.daemon = True
    backup_thread.start()

    # Start the Watchdog observer
    monitor_thread = threading.Thread(target=monitor_files, args=(directory,))
    monitor_thread.daemon = True
    monitor_thread.start()

def send_email_notification(file_count):
    sender_email = "devrathod1307@gmail.com"
    receiver_email = "devnitarathod@gmail.com"
    password = "erfw ihav iozz nlhj"
    smtp_server = "smtp.gmail.com"
    port = 587

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"File Backup Notification - {file_count} files uploaded to S3"
    body = f"{file_count} files have been uploaded to the S3 bucket '{bucket_name}'."
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Notification email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

def upload_to_s3(file_path, email_notifications, file_counter):
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        s3.upload_file(file_path, bucket_name, os.path.basename(file_path))
        
        response = s3.head_object(Bucket=bucket_name, Key=os.path.basename(file_path))
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Successfully uploaded {file_path}")
            file_counter[0] += 1
        else:
            print(f"Upload failed for {file_path}")
        
        # If more than 2 files are uploaded and email notifications are enabled, send an email
        if file_counter[0] > 2 and email_notifications:
            send_email_notification(file_counter[0])
            file_counter[0] = 0  # Reset counter after sending email

    except Exception as e:
        print(f"Error uploading to S3: {e}")

def automate_backup(directory, interval, email_notifications):
    file_counter = [0]  # Counter to track number of files uploaded

    while True:
        for file_path in os.listdir(directory):
            full_path = os.path.join(directory, file_path)
            if os.path.isfile(full_path):
                upload_to_s3(full_path, email_notifications, file_counter)
        
        print(f"Backup completed. Next backup in {interval} hours.")
        messagebox.showinfo("Backup Complete", f"Backup completed. Next backup in {interval} hours.")
        time.sleep(interval * 3600)  # Convert hours to seconds

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, directory, email_notifications, file_counter):
        self.directory = directory
        self.email_notifications = email_notifications
        self.file_counter = file_counter

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"File {event.src_path} has been modified. Starting backup...")
        upload_to_s3(event.src_path, self.email_notifications, self.file_counter)

def monitor_files(directory):
    file_counter = [0]  # Initialize counter
    email_notifications = email_var.get()  # Check if email notifications are enabled

    event_handler = FileChangeHandler(directory, email_notifications, file_counter)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    print(f"Monitoring changes in {directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

app = tk.Tk()
app.title("Automated File Backup System")

# Set window size
app.geometry("400x400")

# Folder selection
folder_button = tk.Button(app, text="Select Folder", command=select_directory)
folder_button.pack(pady=10)
folder_label = tk.Label(app, text="No folder selected")
folder_label.pack()

# Backup interval
interval_label = tk.Label(app, text="Backup Interval (hours):")
interval_label.pack(pady=10)
interval_entry = tk.Entry(app)
interval_entry.pack(pady=10)

# Email notification checkbox
email_var = tk.BooleanVar()
email_checkbox = tk.Checkbutton(app, text="Enable Email Notifications", variable=email_var)
email_checkbox.pack(pady=10)

# Start backup button
start_button = tk.Button(app, text="Save Configuration", command=start_backup)
start_button.pack(pady=20)

app.mainloop()
