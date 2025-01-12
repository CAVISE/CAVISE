import io
import os
import subprocess
import urwid as u
import logging
import pathlib
import importlib


from .common_elements import CommonElements

import cavise.scripts.compose_gen as cg

class ComposeGenView(u.WidgetWrap, CommonElements):
    """View for generating compose configurations and displaying script output.

    Provides an input field for entering parameters, a button to generate the
    compose configurations, a display area for available files, and a scrollable
    area for showing the script output.
    """

    def __init__(self):
        """Initializes the ComposeGenView with input, button, file list, and output widgets."""
        self.input = u.Edit("Enter parameters: ")
        self.file_list = u.Text("")
        self.script_output = u.Text("")
        self.run_button = u.Button("Generate", self.generate, align="center")
        self.update_file_list()

        input_filler = u.Filler(self.input, valign='top')
        file_list_filler = u.Filler(self.file_list, valign='top')
        script_output_filler = self.create_scrollable_script_output(self.script_output)
        button_filler = u.Filler(self.run_button, valign='top')

        pile = u.Pile([
            u.Divider(" "),
            ('weight', 1, input_filler),
            u.Divider("-"),
            ('weight', 1, button_filler),
            u.Divider("-"),
            ('weight', 2, file_list_filler),
            u.Divider("-"),
            ('weight', 2, script_output_filler)
        ])
        u.WidgetWrap.__init__(self, u.Padding(pile, left=5, right=5))

    def keypress(self, size, key):
        """Handle keypress events."""
        if key == 'enter':
            self.generate()
        return super().keypress(size, key)
    
    def generate(self, button=None):
        """Generates the compose configurations by executing a Python script.

        Executes the script with parameters entered by the user, captures the output,
        and updates the script output widget with the result.

        Args:
            button: The button that triggered this action (not used in this method).
        """
        try:
            #command = f"python3 cavise/scripts/compose-gen.py {self.input.get_edit_text()}"
            #result = subprocess.run(command, shell=True, text=True, capture_output=True)
            #output = result.stdout + "\n" + result.stderr
            #output = cg.main()

            pass 
            output = f""

        except Exception as e:
            output = f"Error: {e}"

        self.script_output.set_text(output)
