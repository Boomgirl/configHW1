import os
import tarfile
import json
import toml
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class Emulator:
    def __init__(self, config_path):
        self.current_directory = os.path.dirname( os.path.abspath(__file__))
        self.load_config(config_path)
        self.file_system = {}
        self.load_virtual_file_system()

    def load_config(self, config_path):
        config = toml.load(config_path)
        self.username = config['username']
        self.hostname = config['hostname']
        self.filesystem_path = config['filesystem_path']
        self.log_path = config['log_path']

    def load_virtual_file_system(self):
        with tarfile.open(self.filesystem_path, "r") as tar:
            self.file_system = tar.getnames()
            self.current_directory= "Home"


    def log_action(self, command):
        log_entry = {
            "timestamp": str(datetime.now()),
            "user": self.username,
            "command": command
        }
        with open(self.log_path, 'a') as log_file:
            json.dump(log_entry, log_file)
            log_file.write('\n')

    def execute_command(self, command):
        command_parts = command.split()
        action = command_parts[0]

        if action == "ls":
            return self.cmd_ls()
        elif action == "cd":
            return self.cmd_cd(command_parts[1])
        elif action == "exit":
            exit()
        elif action == "echo":
            return self.cmd_echo(command_parts[1:])
        elif action == "tail":
            return self.cmd_tail(command_parts[1])
        else:
            return "Unknown command."


    def cmd_ls(self):
        self.log_action("ls")
        return '\n'.join(
            name for name in self.file_system
            if name.startswith(self.current_directory + '/') and
            name.count('/') == self.current_directory.count('/') + 1
        )

    def cmd_cd(self, path):
        self.log_action("cd")
        if path in self.file_system:
            self.current_directory = path
            return f"Changed directory to {path}"
        elif self.current_directory + "/" + path  in self.file_system:
            self.current_directory = self.current_directory + "/" + path
            return f"Changed directory to {path}"
        else:
            return "Directory not found."

    def cmd_echo(self, args):
        self.log_action("echo")
        return ' '.join(args)

    def cmd_tail(self, filename):
        self.log_action("tail")
        try:
            with tarfile.open(self.filesystem_path, 'r') as tar:
                member = tar.getmember(self.current_directory + "/" + filename)
                file = tar.extractfile(member)
                lines = file.readlines()
                lines = [line.decode('utf-8') for line in lines]
                return ''.join(lines[-10:])
        except Exception as e:
            return str(e)


class EmulatorGUI:
    def __init__(self, master, emulator):
        self.master = master
        self.emulator = emulator
        master.title("Polina Shell Emulator")

        self.text_area = scrolledtext.ScrolledText(master, width=100, height=30)
        self.text_area.pack()

        self.input_field = tk.Entry(master, width=100)
        self.input_field.pack()
        self.input_field.bind('<Return>', self.process_command)

    def process_command(self, event):
        command = self.input_field.get()
        self.text_area.insert(tk.END, f"{self.emulator.username}@{self.emulator.hostname}: {command}\n")
        output = self.emulator.execute_command(command)
        self.text_area.insert(tk.END, f"{output}\n")
        self.text_area.yview(tk.END)
        self.input_field.delete(0, tk.END)


if __name__ == "__main__":
    config_file = 'config.toml'  # Укажите путь к вашему конфигурационному файлу
    emulator = Emulator(config_file)
    root = tk.Tk()
    gui = EmulatorGUI(root, emulator)
    root.mainloop()