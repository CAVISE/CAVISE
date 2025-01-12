import urwid as u
import subprocess
import docker
from python_on_whales import docker

from .common_elements import CommonElements

import threading
import time

class ComponentView(u.WidgetWrap, CommonElements):
    def __init__(self, component_name, loop):
        self.loop = loop
        self.component_name = component_name
        self.about = u.Text(f"{component_name}")
        self.metrics = u.Text("Info:\n")
        self.logs = u.Text("")
        self.logs_header = u.Text("Logs:")
        self.scrollable_metrics_filler = u.Filler(self.metrics, valign='top')
        self.scrollable_logs_header_filler = u.Filler(self.logs_header)
        self.scrollable_logs_filler = self.create_scrollable_script_output(self.logs)
        self.about_filler = u.Filler(self.about, valign='top')

        pile = u.Pile([
            ('weight', 1, self.about_filler),
            u.Divider("-"),
            ('weight', 1, self.scrollable_metrics_filler),
            u.Divider("-"),
            ('weight', 1, self.scrollable_logs_header_filler),
            ('weight', 1, self.scrollable_logs_filler),
            u.Divider("-"),

        ])

        u.WidgetWrap.__init__(self, pile)

        self.metrics_thread = threading.Thread(target=self.update_metrics, daemon=True)
        self.logs_thread = threading.Thread(target=self.update_logs, daemon=True)
        self.metrics_thread.start()
        self.logs_thread.start()


    def update_metrics(self):
        """Updates metrics in real-time."""
        while True:
            try:
                stat = docker.stats(self.component_name)[0]
                cpu_percentage = stat.cpu_percentage
                memory_percentage = stat.memory_percentage
                memory_used = stat.memory_used
                memory_limit = stat.memory_limit
                net_upload = stat.net_upload
                net_download = stat.net_download

                metrs = "Info:\n"
                metrs += f"CPU Usage (%):        {cpu_percentage}\n"
                metrs += f"Memory Usage (%):     {memory_percentage}\n"
                metrs += f"Memory Used (mb):     {memory_used / 1024}\n"
                metrs += f"Memory Limit (mb):    {memory_limit / 1024}\n"
                metrs += f"Net Upload (bytes):   {net_upload}\n"
                metrs += f"Net Download (bytes): {net_download}"

                self.metrics.set_text(metrs)

                self.loop.draw_screen()

                time.sleep(1)

            except Exception as e:
                self.metrics.set_text(f"Error fetching metrics:\n {e.stderr}")
                self.loop.draw_screen()
                break

    def update_logs(self):
        log = ''
        try:
            output_docker = docker.logs(self.component_name, stream=True)
            for stream_type, stream_content in output_docker:
                log += stream_content.decode()
                self.logs.set_text(log)
                self.loop.draw_screen()

        except Exception as e:
            self.logs.set_text(f"Error fetching logs:\n {e.stderr}")
            self.loop.draw_screen()

