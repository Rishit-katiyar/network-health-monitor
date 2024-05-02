import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import time
import os
import socket
import platform

# Function to get platform-specific commands
def get_platform_command(command):
    if platform.system() == "Windows":
        return command.get("windows", command["default"])
    elif platform.system() == "Darwin":
        return command.get("mac", command["default"])
    else:
        return command["default"]

# Define commands and their corresponding descriptions
COMMANDS = {
    "Ping": {"default": "ping -n 4", "windows": "ping -n 4", "mac": "ping -c 4", "description": "Ping a device to check connectivity. Example: ping google.com"},
    "IPConfig": {"default": "ipconfig /all", "windows": "ipconfig /all", "mac": "ifconfig", "description": "Display IP configuration. Example: ipconfig /all"},
    "TaskList": {"default": "tasklist", "windows": "tasklist", "mac": "ps -A", "description": "List all running tasks. Example: tasklist"},
    "TaskKill": {"default": "taskkill /F /PID", "windows": "taskkill /F /PID", "mac": "kill", "description": "Terminate a task by PID. Example: taskkill /F /PID 1234"},
    "NetUse": {"default": "net use", "windows": "net use", "mac": "mount", "description": "Display network drive mappings. Example: net use"},
    "SFC": {"default": "sfc /scannow", "windows": "sfc /scannow", "mac": "N/A", "description": "Scan and repair system files. Example: sfc /scannow"},
    "CHKDSK": {"default": "chkdsk /f", "windows": "chkdsk /f", "mac": "diskutil verifyDisk", "description": "Check disk for errors and repair them. Example: chkdsk /f"},
    "DiskPart": {"default": "diskpart", "windows": "diskpart", "mac": "diskutil", "description": "Disk partitioning tool. Example: diskpart"},
    "BCDEdit": {"default": "bcdedit", "windows": "bcdedit", "mac": "N/A", "description": "Boot Configuration Data editor. Example: bcdedit"},
    "WMIC": {"default": "wmic cpu get name", "windows": "wmic cpu get name", "mac": "sysctl -n machdep.cpu.brand_string", "description": "Display CPU information. Example: wmic cpu get name"},
    "Robocopy": {"default": "robocopy", "windows": "robocopy", "mac": "rsync", "description": "Robust file copy tool. Example: robocopy source destination"},
    "SCHTasks": {"default": "schtasks /query", "windows": "schtasks /query", "mac": "crontab -l", "description": "Display scheduled tasks. Example: schtasks /query"},
    "SystemInfo": {"default": "systeminfo", "windows": "systeminfo", "mac": "system_profiler", "description": "Display system information. Example: systeminfo"}
}

# Define commands that do not require an IP address or hostname
NO_DEVICE_COMMANDS = ["IPConfig", "NetStat", "SystemInfo"]

# Define colors for visualization
COLOR_GREEN = "#00FF00"
COLOR_RED = "#FF0000"

# Define GUI class
class NetworkHealthMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Health Monitor")
        self.geometry("800x600")

        # Get local IP address
        local_ip = socket.gethostbyname(socket.gethostname())

        # Create device input section
        self.device_label = ttk.Label(self, text="Enter IP Addresses or Hostnames (comma-separated):")
        self.device_entry = ttk.Entry(self, width=50)
        self.device_entry.insert(0, local_ip)  # Populate with local IP by default
        self.device_label.pack(pady=10)
        self.device_entry.pack(pady=5)

        # Create command selection dropdown
        self.command_label = ttk.Label(self, text="Select Command:")
        self.command_combo = ttk.Combobox(self, values=list(COMMANDS.keys()), width=40)
        self.command_combo.set("Ping")  # Default command
        self.command_label.pack(pady=10)
        self.command_combo.pack(pady=5)

        # Create run button
        self.run_button = ttk.Button(self, text="Run Command", command=self.run_command)
        self.run_button.pack(pady=10)

        # Create exit button
        self.exit_button = ttk.Button(self, text="Exit", command=self.quit)
        self.exit_button.pack(pady=10)

        # Create output text area
        self.output_text = ScrolledText(self, height=20, width=100, wrap=tk.WORD)
        self.output_text.pack(pady=10)

        # Create loading screen
        self.loading_screen = None

    def run_command(self):
        command_name = self.command_combo.get()
        command_info = COMMANDS.get(command_name)
        devices = self.device_entry.get().split(",")

        # Clear output text
        self.output_text.delete('1.0', tk.END)

        # Check if the command requires a device input
        if command_name not in NO_DEVICE_COMMANDS and not self.device_entry.get():
            messagebox.showerror("Error", "Please provide IP Addresses or Hostnames for this command.")
            return

        # Show loading screen
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.show()

        # Execute command for each device
        for device in devices:
            if command_name in NO_DEVICE_COMMANDS:
                device = ""  # Reset device for commands that do not require it
            command = get_platform_command(command_info)
            output = self.execute_command(command, device.strip())
            # Add output to text area and colorize based on success/failure
            if "Error" in output:
                self.display_output(f"Output for {device} ({command_name}):", output, color=COLOR_RED)
            else:
                self.display_output(f"Output for {device} ({command_name}):", output, color=COLOR_GREEN)

        # Hide loading screen
        if self.loading_screen:
            self.loading_screen.hide()

    def execute_command(self, command, device):
        try:
            # Execute command using subprocess with timeout
            process = subprocess.Popen(f"{command} {device}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate(timeout=30)  # Timeout set to 30 seconds
            if error:
                return f"Error occurred: {error.decode()}"
            return output.decode()
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error occurred: {str(e)}"

    def display_output(self, title, output, color=None):
        # Apply color if specified
        if color:
            self.output_text.tag_configure("colored", foreground=color)
            self.output_text.insert(tk.END, f"{title}\n", "colored")
        else:
            self.output_text.insert(tk.END, f"{title}\n")
            
        # Insert output into text area
        self.output_text.insert(tk.END, output)
        self.output_text.insert(tk.END, "\n\n")

# Define loading screen class
class LoadingScreen:
    def __init__(self, parent):
        self.parent = parent
        self.loading_window = None

    def show(self):
        self.loading_window = tk.Toplevel(self.parent)
        self.loading_window.geometry("200x100")
        self.loading_window.title("Loading...")
        label = tk.Label(self.loading_window, text="Executing command...")
        label.pack()

    def hide(self):
        if self.loading_window:
            self.loading_window.destroy()

# Main function
def main():
    app = NetworkHealthMonitor()
    app.mainloop()

if __name__ == "__main__":
    main()
