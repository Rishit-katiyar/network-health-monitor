import unittest
from unittest.mock import patch
from tkinter import Tk
from network_health_monitor import NetworkHealthMonitor, COMMANDS, COLOR_GREEN, COLOR_RED

class TestNetworkHealthMonitor(unittest.TestCase):
    def setUp(self):
        self.app = NetworkHealthMonitor()
        self.app.withdraw()  # Hide the Tkinter window during tests

    def tearDown(self):
        self.app.destroy()

    def test_execute_command_success(self):
        # Test execute_command method for successful execution
        output = self.app.execute_command("echo Hello", "")
        self.assertEqual(output.strip(), "Hello")

    def test_execute_command_timeout(self):
        # Test execute_command method for timeout
        output = self.app.execute_command("sleep 10", "")
        self.assertEqual(output, "Error: Command timed out after 30 seconds.")

    def test_execute_command_exception(self):
        # Test execute_command method for generic exception
        output = self.app.execute_command("non_existing_command", "")
        self.assertTrue("Error occurred" in output)

    def test_display_output_success(self):
        # Test display_output method for success
        with patch.object(self.app.output_text, 'insert') as mock_insert:
            self.app.display_output("Title", "Output", color=COLOR_GREEN)
            mock_insert.assert_called_with(Tk.END, "Title\n", 'colored')
            mock_insert.assert_called_with(Tk.END, "Output\n")

    def test_display_output_failure(self):
        # Test display_output method for failure
        with patch.object(self.app.output_text, 'insert') as mock_insert:
            self.app.display_output("Title", "Error", color=COLOR_RED)
            mock_insert.assert_called_with(Tk.END, "Title\n", 'colored')
            mock_insert.assert_called_with(Tk.END, "Error\n")

    @patch('network_health_monitor.socket.gethostbyname')
    def test_init_with_default_local_ip(self, mock_gethostbyname):
        # Test initialization with default local IP
        mock_gethostbyname.return_value = "192.168.0.1"
        app = NetworkHealthMonitor()
        self.assertEqual(app.device_entry.get(), "192.168.0.1")

    def test_run_command_no_device_input(self):
        # Test run_command method when no device input provided
        with patch.object(self.app, 'execute_command') as mock_execute:
            self.app.device_entry.delete(0, Tk.END)
            self.app.run_command()
            mock_execute.assert_not_called()

    def test_run_command_success(self):
        # Test run_command method for successful execution
        with patch.object(self.app, 'execute_command') as mock_execute:
            mock_execute.return_value = "Output"
            self.app.run_command()
            mock_execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
