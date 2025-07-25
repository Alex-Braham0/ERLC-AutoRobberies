#!/usr/bin/python3.11

import tkinter as tk
from tkinter import scrolledtext
from tkinter import *
from tkinter.ttk import *
# import time
# import numpy as np
# import pyautogui
# import pydirectinput
# import datetime
# import statistics
import os
import os.path
import importlib.util
import sys
import threading

class GuiOutputRedirector:
    def __init__(self, write_func):
        self.write_func = write_func

    def write(self, text):
        text = text.strip()
        if text:
            self.write_func(text)

    def flush(self):
        pass  # Required for file-like compatibility

class AutoRobbery:
    def __init__(self, root):
        self.launching = True
        self.root = root
        self.root.title("ERLC Auto Robbery")
        self.process = None

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=45, height=12)
        self.output_text.pack(padx=10, pady=10)

        # Set the ScrolledText widget as read-only
        self.output_text.configure(state=tk.DISABLED)

        self.scripts_location = "Scripts"
        self.load_scripts()
        
        self.launching = False
        self.update_output("Loading complete")
        self.update_output("Welcome to ERLC Auto Robbery\nPlease select a robbery to complete:")

        quit_button = tk.Button(root, text="Quit", command=self.root.destroy)
        quit_button.pack(pady=5)

        # Set the window to stay on top
        self.set_window_always_on_top()

    def load_scripts(self):
        self.robberies = {}

        if os.path.isdir(self.scripts_location):
            for script_path in [os.path.join(self.scripts_location, file) for file in os.listdir(self.scripts_location) if file.endswith(".py") and not file.endswith("_hidden.py")]:
                script_name = os.path.splitext(os.path.basename(script_path))[0]  # 'MyClass'

                spec = importlib.util.spec_from_file_location(script_name, script_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                cls = getattr(mod, script_name)
                self.robberies[cls.name] = {
                    "script": cls(),
                    "button": tk.Button(root, text=f"Run {cls.name} Script", command=lambda s=cls.name: self.run_script(s))}
                if hasattr(cls, "cooldown"):
                    self.robberies[cls.name]["current_cooldown"] = 0
                    self.robberies[cls.name]["bar"] = Progressbar(root, orient = HORIZONTAL, length = 250, mode = 'determinate')
                self.robberies[cls.name]["bar"].pack(pady=1)
                self.robberies[cls.name]["button"].pack(pady=10)
                self.update_output(f"Loaded {cls.name}...")
        else:
            self.update_output(f"Scripts location not found: {self.scripts_location}")

    def set_window_always_on_top(self):
        self.root.wm_attributes("-topmost", 1)
        self.root.after(100, self.set_window_always_on_top)

    def run_script(self, script_name):        
        # Check if a script is already running
        if self.launching:
            return
        if self.process:
            self.update_output("Another script is currently running. Please wait until it finishes.")
            return
        elif self.robberies[script_name]["current_cooldown"]:
            self.update_output("Robbery is currently on Cooldown. Please wait for progress bar to clear.")
            return

        self.update_output(f"\n--- Running {script_name} ---\n")

        def threaded_run():
            # Redirect stdout to GUI
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = GuiOutputRedirector(self.update_output)
            sys.stderr = GuiOutputRedirector(self.update_output)
            try:
                self.process = True
                successful = self.robberies[script_name]["script"].run()
                self.process = False
                if successful and hasattr(self.robberies[script_name]["script"], "cooldown"):
                    self.cooldown(script_name)
            except Exception as e:
                self.update_output(f"Error: {e}")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        self.script_thread = threading.Thread(target=threaded_run, daemon=True)
        self.script_thread.start()

    def cooldown(self, script_name):
        if self.robberies[script_name]["current_cooldown"] > 99.9:
            self.robberies[script_name]["current_cooldown"] = 0
            self.update_output(f"{script_name} COOLDOWN CLEARED")
        else:
            self.robberies[script_name]["current_cooldown"] += 100/self.robberies[script_name]["script"].cooldown
            self.root.after(1000, lambda: self.cooldown(script_name))
        self.robberies[script_name]["bar"]["value"] = self.robberies[script_name]["current_cooldown"]

    def update_output(self, text):
        # Ensure that the ScrolledText widget is in NORMAL state before modifying its content
        self.output_text.configure(state=tk.NORMAL)
        # self.output_text.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M')} - {text}\n")
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)
        # Set the ScrolledText widget back to read-only state
        self.output_text.configure(state=tk.DISABLED)

        # Update the GUI immediately
        self.root.update_idletasks()

    def clear_output(self):
        # Ensure that the ScrolledText widget is in NORMAL state before clearing its content
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        # Set the ScrolledText widget back to read-only state
        self.output_text.configure(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoRobbery(root)
    root.mainloop()