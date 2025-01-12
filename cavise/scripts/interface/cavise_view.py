import os
import queue
import threading
import subprocess
import urwid as u
from python_on_whales import DockerClient
 

from .common_elements import CommonElements

class CAVISEView(u.WidgetWrap, CommonElements):
    """A view for interacting with Docker Compose commands in the CAVISE environment.

    This view allows users to select a file from a list of available files, specify
    custom parameters, choose services to start, and execute Docker Compose commands 
    (up, down, build, restart). The output of the commands is displayed in a scrollable 
    text area.
    """

    def __init__(self, loop):
        """Initializes the CAVISEView with input fields, buttons, and output area."""
        self.is_docker_action_in_progress = False
        self.loop = loop
        self.file_list = u.Text("")
        self.update_file_list()
        
        self.ls_output_text = self.file_list
        self.file_selector = u.Edit("Select File: ")
        self.file_selector.set_edit_text(self.files[0] if self.files else "")
        
        self.custom_params_input = u.Edit("Custom Parameters: ")
        self.services_from_input = u.Edit("Select Services (default: only main sim): ")
        self.script_output = u.Text("")

        self.build_button = u.Button("Build", self.on_build_button_pressed, align="center")
        self.up_button = u.Button("Up", self.on_up_button_pressed, align="center")
        self.down_button = u.Button("Down", self.on_down_button_pressed, align="center")
        self.restart_button = u.Button("Restart", self.on_restart_button_pressed, align="center")

        ls_filler = u.Filler(self.ls_output_text, valign='top')
        file_filler = u.Filler(self.file_selector, valign='top')
        params_filler = u.Filler(self.custom_params_input, valign='top')
        services_filler = u.Filler(self.services_from_input, valign='top')
        self.output_filler = self.create_scrollable_script_output(self.script_output) 
        build_filler = u.Filler(self.build_button, valign='top')
        up_filler = u.Filler(self.up_button, valign='top')
        down_filler = u.Filler(self.down_button, valign='top')
        restart_filler = u.Filler(self.restart_button, valign='top')

        pile = u.Pile([
            u.Divider(" "),
            ('weight', 2, ls_filler),
            u.Divider("-"),
            ('weight', 1, file_filler),
            u.Divider("-"),
            ('weight', 1, params_filler),
            u.Divider("-"),
            ('weight', 1, services_filler),
            u.Divider("-"),
            ('weight', 1, build_filler),
            u.Divider("-"),
            ('weight', 1, up_filler),
            u.Divider("-"),
            ('weight', 1, down_filler),
            u.Divider("-"),
            ('weight', 1, restart_filler),
            u.Divider("-"),
            ('weight', 2, self.output_filler)
        ])
        
        u.WidgetWrap.__init__(self, u.Padding(pile, left=5, right=5))
    
    # It is for blocking the interface while the Docker thread is running
    def on_up_button_pressed(self, button):
        if not self.is_docker_action_in_progress:
            self.run_up(button)

    def on_build_button_pressed(self, button):
        if not self.is_docker_action_in_progress:
            self.run_build(button)

    def on_restart_button_pressed(self, button):
        if not self.is_docker_action_in_progress:
            self.run_restart(button)

    def on_down_button_pressed(self, button):
        if not self.is_docker_action_in_progress:
            self.run_down(button)


    def docker_up_thread(self, docker, params, services_to_up, log_queue):
        try:
            output_docker = docker.compose.up(
                services={services_to_up} if services_to_up else None,
                build=params["build"],
                detach=params["detach"],
                abort_on_container_exit=params["abort_on_container_exit"],
                scales=params["scales"],
                attach_dependencies=params["attach_dependencies"],
                force_recreate=params["force_recreate"],
                recreate=params["recreate"],
                no_build=params["no_build"],
                remove_orphans=params["remove_orphans"],
                renew_anon_volumes=params["renew_anon_volumes"],
                color=params["color"],
                log_prefix=params["log_prefix"],
                start=params["start"],
                quiet=params["quiet"],
                wait=params["wait"],
                no_attach_services=params["no_attach_services"],
                pull=params["pull"],
                stream_logs=params["stream_logs"],
                wait_timeout=params["wait_timeout"]
            )

            if output_docker:
                for stream_type, stream_content in output_docker:
                    log_queue.put(stream_content.decode())
            else:
                log_queue.put("No output from Docker compose restart.\n")

            log_queue.put("Command finished successfully.\n")
        except Exception as e:
            log_queue.put(f"Error: {e}\n")
        finally:
            log_queue.task_done()

    def docker_build_thread(self, docker, params, services_to_build, log_queue):
        try:
            output_docker = docker.compose.build(
                services={services_to_build} if services_to_build else None,
                build_args=params["build_args"],
                cache=params["cache"],
                pull=params["pull"],
                quiet=params["quiet"],
                ssh=params["ssh"],
                stream_logs=True
            )

            if output_docker:
                for stream_type, stream_content in output_docker:
                    log_queue.put(stream_content.decode())
            else:
                log_queue.put("No output from Docker compose restart.\n")

            log_queue.put("Command finished successfully.\n")
        except Exception as e:
            log_queue.put(f"Error: {e}\n")
        finally:
            log_queue.task_done()
    
    def docker_down_thread(self, docker, params, services_to_stop, log_queue):
        try:
            output_docker = docker.compose.down(
                services={services_to_stop} if services_to_stop else None,
                remove_orphans=params["remove_orphans"],
                remove_images=params["remove_images"],
                timeout=params["timeout"],
                volumes=params["volumes"],
                quiet=params["quiet"],
                stream_logs=True
            )

            if output_docker:
                for stream_type, stream_content in output_docker:
                    log_queue.put(stream_content.decode())
            else:
                log_queue.put("No output from Docker compose restart.\n")

            log_queue.put("Command finished successfully.\n")
        except Exception as e:
            log_queue.put(f"Error: {e}\n")
        finally:
            log_queue.task_done()

    def docker_restart_thread(self, docker, params, services_to_restart, log_queue):
        try:
            output_docker = docker.compose.restart(
                services={services_to_restart} if services_to_restart else None,
                timeout=params["timeout"],
            )
            if output_docker:
                for stream_type, stream_content in output_docker:
                    log_queue.put(stream_content.decode())
            else:
                log_queue.put("No output from Docker compose restart.\n")

            log_queue.put("Command finished successfully.\n")
        except Exception as e:
            log_queue.put(f"Error: {e}\n")
        finally:
            log_queue.task_done()


    def log_updater(self, log_queue):
        while True:
            try:
                log = log_queue.get(timeout=1)
                if log is None:
                    break
                current_output = str(self.script_output.get_text()[0]).replace('\\', "")
                updated_output = f"{current_output}{log.replace('\\', '')}"
                self.script_output.set_text(updated_output)

                self.output_filler = self.create_scrollable_script_output(self.script_output)
                self.loop.draw_screen()
            except queue.Empty:
                continue


    def run_build(self, button):
        """Executes the 'docker compose build' command based on user input.

        Args:
            button: The button that triggered this action.
        """
        try:
            self.is_docker_action_in_progress = True # For UI blocking
            selected_file = self.file_selector.get_edit_text()
            custom_params = self.custom_params_input.get_edit_text().split()
            services_to_build = self.services_from_input.get_edit_text()
            docker = DockerClient(compose_files=[f"./dc-configs/{selected_file}"])

            params = {
                "build_args": {},
                "builder": None,
                "dry_run": False,
                "memory": None,
                "cache": True,
                "pull": False,
                "quiet": False,
                "ssh": None,
            }


            self.is_docker_action_in_progress = True
            i = 0
            while i < len(custom_params):
                if custom_params[i] == "--build-args":
                    i += 1
                    while i < len(custom_params) and "=" in custom_params[i]:
                        key, value = custom_params[i].split("=")
                        params["build_args"][key] = value
                        i += 1
                elif custom_params[i] == "--no-cache":
                    params["cache"] = False
                    i += 1
                elif custom_params[i] == "--pull":
                    params["pull"] = True
                    i += 1
                elif custom_params[i] == "--quiet":
                    params["quiet"] = True
                    i += 1
                elif custom_params[i] == "--ssh":
                    params["ssh"] = custom_params[i + 1]
                    i += 2
                else:
                    raise ValueError(f"Unknown parameter: {custom_params[i]}")
                    i += 1

            self.script_output.set_text("Build is running...")
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
            self.loop.draw_screen()

            log_queue = queue.Queue()

            docker_thread = threading.Thread(target=self.docker_build_thread, args=(docker, params, services_to_build, log_queue), daemon=True)
            docker_thread.start()

            log_updater_thread = threading.Thread(target=self.log_updater, args=(log_queue,), daemon=True)
            log_updater_thread.start()

        except Exception as e:
            output = f"Error: {e}"
            self.script_output.set_text(output)
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
        finally:
            self.is_docker_action_in_progress = False

    def run_up(self, button):
        """Executes the 'docker compose up' command based on user input.

        Args:
            button: The button that triggered this action.
        """
        try:
            self.is_docker_action_in_progress = True # For UI blocking
            selected_file = self.file_selector.get_edit_text()
            custom_params = self.custom_params_input.get_edit_text()
            services_to_up = self.services_from_input.get_edit_text()
            docker = DockerClient(compose_files=[f"./dc-configs/{selected_file}"])
            
            params = {
            "build": False,
            "detach": True,
            "abort_on_container_exit": False,
            "scales": {},
            "attach_dependencies": False,
            "force_recreate": False,
            "recreate": True,
            "no_build": False,
            "remove_orphans": False,
            "renew_anon_volumes": False,
            "color": True,
            "log_prefix": True,
            "start": True,
            "quiet": False,
            "wait": False,
            "no_attach_services": None,
            "pull": None,
            "stream_logs": True,
            "wait_timeout": None,
        }


            i = 0
            while i < len(custom_params):
                if custom_params[i] == "--build":
                    params["build"] = True
                    i += 1
                elif custom_params[i] == "--abort-on-container-exit":
                    params["abort_on_container_exit"] = True
                    i += 1
                elif custom_params[i] == "--scales":
                    i += 1
                    scales_input = custom_params[i].split(",")
                    for scale in scales_input:
                        service, num = scale.split("=")
                        params["scales"][service] = int(num)
                    i += 1
                elif custom_params[i] == "--attach-dependencies":
                    params["attach_dependencies"] = True
                    i += 1
                elif custom_params[i] == "--force-recreate":
                    params["force_recreate"] = True
                    i += 1
                elif custom_params[i] == "--recreate":
                    params["recreate"] = custom_params[i + 1].lower() == "true"
                    i += 2
                elif custom_params[i] == "--no-build":
                    params["no_build"] = True
                    i += 1
                elif custom_params[i] == "--remove-orphans":
                    params["remove_orphans"] = True
                    i += 1
                elif custom_params[i] == "--renew-anon-volumes":
                    params["renew_anon_volumes"] = True
                    i += 1
                elif custom_params[i] == "--color":
                    params["color"] = custom_params[i + 1].lower() == "true"
                    i += 2
                elif custom_params[i] == "--log-prefix":
                    params["log_prefix"] = custom_params[i + 1].lower() == "true"
                    i += 2
                elif custom_params[i] == "--start":
                    params["start"] = custom_params[i + 1].lower() == "true"
                    i += 2
                elif custom_params[i] == "--quiet":
                    params["quiet"] = True
                    i += 1
                elif custom_params[i] == "--wait":
                    params["wait"] = True
                    i += 1
                elif custom_params[i] == "--no-attach-services":
                    params["no_attach_services"] = custom_params[i + 1].split(",")
                    i += 2
                elif custom_params[i] == "--pull":
                    params["pull"] = custom_params[i + 1]
                    i += 2
                elif custom_params[i] == "--stream-logs":
                    params["stream_logs"] = True
                    i += 1
                elif custom_params[i] == "--wait-timeout":
                    params["wait_timeout"] = int(custom_params[i + 1])
                    i += 2
                else:
                    raise ValueError(f"Unknown parameter: {custom_params[i]}")
                    i += 1

            self.script_output.set_text("Up -d command is running...\n")
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
            self.loop.draw_screen()

            log_queue = queue.Queue()

            docker_thread = threading.Thread(target=self.docker_up_thread, args=(docker, params, services_to_up, log_queue), daemon=True)
            docker_thread.start()

            log_updater_thread = threading.Thread(target=self.log_updater, args=(log_queue,), daemon=True)
            log_updater_thread.start()
        
        except Exception as e:
            output = f"Error: {e}"
            self.script_output.set_text(output)
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
        finally:
            self.is_docker_action_in_progress = False

    def run_down(self, button):
        """Executes the 'docker compose down' command based on user input.

        Args:
            button: The button that triggered this action.
        """
        try:
            self.is_docker_action_in_progress = True # For UI blocking

            selected_file = self.file_selector.get_edit_text()
            custom_params = self.custom_params_input.get_edit_text()
            services_to_stop = self.services_from_input.get_edit_text()
            docker = DockerClient(compose_files=[f"./dc-configs/{selected_file}"])

            params = {
                "remove_orphans": False,
                "remove_images": None,
                "timeout": None,
                "volumes": False,
                "quiet": False,
            }


            
            i = 0
            while i < len(custom_params):
                if custom_params[i] == "--remove-orphans":
                    params["remove_orphans"] = True
                    i += 1
                elif custom_params[i] == "--remove-images":
                    if i + 1 < len(custom_params):
                        params["remove_images"] = custom_params[i + 1]
                        i += 2
                    else:
                        raise ValueError("Missing value for --remove-images")
                elif custom_params[i] == "--timeout":
                    if i + 1 < len(custom_params):
                        params["timeout"] = int(custom_params[i + 1])
                        i += 2
                    else:
                        raise ValueError("Missing value for --timeout")
                elif custom_params[i] == "--volumes":
                    params["volumes"] = True
                    i += 1
                elif custom_params[i] == "--quiet":
                    params["quiet"] = True
                    i += 1
                else:
                    raise ValueError(f"Unknown parameter: {custom_params[i]}")
                    i += 1

            self.script_output.set_text("Docker compose down is running...")
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
            self.loop.draw_screen()
        
            log_queue = queue.Queue()

            docker_thread = threading.Thread(target=self.docker_down_thread, args=(docker, params, services_to_stop, log_queue), daemon=True)
            docker_thread.start()

            log_updater_thread = threading.Thread(target=self.log_updater, args=(log_queue,), daemon=True)
            log_updater_thread.start()
        except Exception as e:
            output = f"Error: {e}"

            self.script_output.set_text(output)
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
        finally:
            self.is_docker_action_in_progress = False

    def run_restart(self, button):
        """Executes the 'docker compose restart' command based on user input.

        Args:
            button: The button that triggered this action.
        """
        try:
            self.is_docker_action_in_progress = True # For UI blocking
            selected_file = self.file_selector.get_edit_text()
            custom_params = self.custom_params_input.get_edit_text()
            services_to_restart = self.services_from_input.get_edit_text()
            docker = DockerClient(compose_files=[f"./dc-configs/{selected_file}"])
            
            params = {
                "services": None,
                "timeout": None,
            }

            i = 0
            while i < len(custom_params):
                if custom_params[i] == "--timeout":
                    if i + 1 < len(custom_params):
                        params["timeout"] = int(custom_params[i + 1])
                        i += 2
                    else:
                        raise ValueError("Missing value for --timeout")
                else:
                    raise ValueError(f"Unknown parameter: {custom_params[i]}")
                    i += 1
            
            self.script_output.set_text("Docker compose restart is running...\n")
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
            self.loop.draw_screen()

            log_queue = queue.Queue()

            docker_thread = threading.Thread(target=self.docker_restart_thread, args=(docker, params, services_to_restart, log_queue), daemon=True)
            docker_thread.start()

            log_updater_thread = threading.Thread(target=self.log_updater, args=(log_queue,), daemon=True)
            log_updater_thread.start()

        except Exception as e:
            output = f"Error: {e}"

            self.script_output.set_text(output)
            self.output_filler = self.create_scrollable_script_output(self.script_output) 
        finally:
            self.is_docker_action_in_progress = False