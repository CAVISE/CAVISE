import urwid as u
import threading
import subprocess
import time
import docker
import platform
import psutil
import GPUtil
import vulkan
from python_on_whales import DockerClient
from .common_elements import CommonElements


class InfoView(u.WidgetWrap, CommonElements):
    def __init__(self, loop):
        self.loop = loop
        self.text = u.Text("Status Content")
        self.container_names = ["artery", "carla", "opencda", "scenario-manager"]
        self.status_output = "Containers status\n"
        self.client = docker.from_env()

        self.status_thread = threading.Thread(target=self.update_statuses, daemon=True)
        self.status_thread.start()

        u.WidgetWrap.__init__(self, u.Padding(self.create_scrollable_script_output(self.text), left=5, right=2))

    def update_statuses(self):
        """Real-time updates of container statuses and hardware info."""
        while True:
            self.status_output = "Containers status\n"

            self.update_status_carla()
            self.update_status_opencda()
            self.update_status_artery()
            self.update_status_scmn()

            self.update_docker_status()
            self.update_hardware_status()

            self.text.set_text(self.status_output)
            self.loop.draw_screen()

            time.sleep(1)

    def update_docker_status(self):
        try:
            docker = DockerClient()
            docker_version = docker.version().client.version
            compose_version = docker.compose.version()
            
            self.status_output += f"\nDocker version:         {docker_version}\n"
            self.status_output += f"Docker Compose version: {compose_version}\n"

        except Exception as e:
            self.status_output += f"Docker Error: {e}\n"

    def update_hardware_status(self):
        try:
            cpu_info = platform.processor()
            cpu_count = psutil.cpu_count(logical=False)
            logical_cpu_count = psutil.cpu_count(logical=True)

            self.status_output += "\nCPU Information:\n"
            self.status_output += f"Processor:      {cpu_info}\n"
            self.status_output += f"Physical Cores: {cpu_count}\n"
            self.status_output += f"Logical Cores:  {logical_cpu_count}\n"

            memory_info = psutil.virtual_memory()

            self.status_output += "\nMemory Information:\n"
            self.status_output += f"Total Memory:     {memory_info.total / 1024 / 1024} MB\n"
            self.status_output += f"Available Memory: {memory_info.available / 1024 / 1024} MB\n"
            self.status_output += f"Used Memory:      {memory_info.used / 1024 / 1024} MB\n"

            gpus = GPUtil.getGPUs()

            if not gpus:
                self.status_output += "\nNo GPU detected.\n"
            else:
                for i, gpu in enumerate(gpus):
                    self.status_output += f"\nGPU {i + 1} Information:\n"
                    self.status_output += f"ID:               {gpu.id}\n"
                    self.status_output += f"Name:             {gpu.name}\n"
                    self.status_output += f"Driver:           {gpu.driver}\n"
                    self.status_output += f"GPU Memory Total: {gpu.memoryTotal} MB\n"
                    self.status_output += f"GPU Memory Free:  {gpu.memoryFree} MB\n"
                    self.status_output += f"GPU Load:         {gpu.load * 100}%\n"
                    self.status_output += f"GPU Temperature:  {gpu.temperature}°C\n"

            try:
                version = vulkan.vkEnumerateInstanceVersion()
                major = (version >> 22) & 0x3FF
                minor = (version >> 12) & 0x3FF
                patch = version & 0xFFF
                self.status_output += f"Vulkan version:   {major}.{minor}.{patch}"
            except Exception as e:
                self.status_output += f"Error getting Vulkan version: {e}"

        except Exception as e:
            self.status_output += f"Hardware Error: {e}\n"

    def update_status_scmn(self, container="scenario-manager"):
        try:
            check_command = f"docker ps --filter 'name={container}' --format '{{{{.Names}}}}'"
            result = subprocess.run(check_command, shell=True, text=True, capture_output=True)
            if result.stdout.strip():
                command_check_process = (
                    f"docker exec {container} pgrep -f 'python main.py' > /dev/null 2>&1 && echo 'Healthy. Scenario Manager is running' || echo 'Unhealthy. Scenario Manager is not running'"
                )
                result_process = subprocess.run(command_check_process, shell=True, text=True, capture_output=True)
                health_status = result_process.stdout.strip()
            else:
                health_status = "Container not running."

            self.status_output += f"{container}: {health_status}\n"

        except Exception as e:
            self.status_output += f"{container}: Error - {e}\n"

    def update_status_carla(self, container="carla"):
        try:
            check_command = f"docker ps --filter 'name={container}' --format '{{{{.Names}}}}'"
            result = subprocess.run(check_command, shell=True, text=True, capture_output=True)
            if result.stdout.strip():
                command_check_process = (
                    f"docker exec {container} pgrep -f 'CarlaUE4.sh' > /dev/null 2>&1 && echo 'Healthy. The process CarlaUE4.sh is running' || echo 'Unhealthy. The process CarlaUE4.sh is not running'"
                )
                result_process = subprocess.run(command_check_process, shell=True, text=True, capture_output=True)
                health_status = result_process.stdout.strip()
            else:
                health_status = "Container not running."

            self.status_output += f"{container}: {health_status}\n"

        except Exception as e:
            self.status_output += f"{container}: Error - {e}\n"
          
    def update_status_opencda(self, container="opencda"):
        try:
            check_command = f"docker ps --filter 'name={container}' --format '{{{{.Names}}}}'"
            result = subprocess.run(check_command, shell=True, text=True, capture_output=True)
            if result.stdout.strip():
                command_check_process = (
                    f"docker exec {container} pgrep -f 'opencda.py|python' > /dev/null 2>&1 && "
                    f"docker exec {container} ps aux | grep -E 'opencda.py|python' | awk '{{print $11, $12, $13, $14}}' | grep -v grep || echo 'Waiting. No scenario is running'"
                )

                result_process = subprocess.run(command_check_process, shell=True, text=True, capture_output=True)
                health_status = result_process.stdout.strip()

                if "Waiting" in health_status:
                    health_status = "Waiting. No scenario is running"
                else:
                    command_line = result_process.stdout.strip().split("\n")[0]
                    health_status = f"Healthy. The process opencda.py is running. Scenario: {command_line}"
            else:
                health_status = "Container not running."
            
            self.status_output += f"{container}: {health_status}\n"

        except Exception as e:
            self.status_output += f"{container}: Error - {e}\n"
        
    def update_status_artery(self, container="artery"):
        try:
            check_command = f"docker ps --filter 'name={container}' --format '{{{{.Names}}}}'"
            result = subprocess.run(check_command, shell=True, text=True, capture_output=True)

            if result.stdout.strip():
                command_check_process = (
                    f"docker exec {container} pgrep -f 'make run_' > /dev/null 2>&1 && "
                    f"docker exec {container} ps aux | grep 'make run_' | grep -v grep || echo 'Waiting. No scenario is running'"
                )
                result_process = subprocess.run(command_check_process, shell=True, text=True, capture_output=True)
                health_status = result_process.stdout.strip()

                if "Waiting" in health_status:
                    health_status = "Waiting. No scenario is running"
                else:

                    command_line = result_process.stdout.strip().split("\n")[0]
                    health_status = f"Healthy. The scenario is running. Command - {command_line}"
            else:
                health_status = "Container not running."

            self.status_output += f"{container}: {health_status}\n"

        except Exception as e:
            self.status_output += f"{container}: Error - {e}\n"
