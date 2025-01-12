import os
import subprocess
import urwid as u
import requests
import json

class ScenarioManagerView(u.WidgetWrap):
    """View for managing scenarios with request input and response output.

    Provides an input field for a user to enter a command, a button to execute
    the command, and an output area to display the result or error message.
    """

    def __init__(self):
        """Initializes the ScenarioManagerView with input, button, and output widgets."""
        self.text = u.Text("Scenario Content")

        self.response_output = u.Text("Response:", wrap='space')
        self.send_button = u.Button("Send!", self.run_command, align="center")

        self.url = u.Edit("API URL:\n", wrap='space', multiline="True")
        self.headers = u.Edit("Headers:\n", wrap='space', multiline="True")
        self.data = u.Edit("Data:\n", wrap='space', multiline="True")
        url_filler = u.Filler(self.url, valign='top')
        headers_filler = u.Filler(self.headers, valign='top')
        data_filler = u.Filler(self.data, valign='top')
        response_filler = u.Filler(self.response_output, valign='top')
        send_filler = u.Filler(self.send_button, valign='top')

        pile = u.Pile([
            u.Divider(" "),
            ('weight', 2, url_filler),
            u.Divider("-"),
            ('weight', 2, headers_filler),
            u.Divider("-"),
            ('weight', 2, data_filler),
            u.Divider("-"),
            ('weight', 1, send_filler),
            u.Divider("-"),
            ('weight', 1, response_filler),
            u.Divider("-"),
        ])
        
        u.WidgetWrap.__init__(self, u.Padding(pile, left=5, right=5))

    
    def run_command(self, button=None):
        """Executes the command entered in the request input field and displays the output.

        Args:
            button: The button that triggered this action (not used in this method).
        """


        try:
            url = f"http://8.8.0.8:8999/{self.url.get_edit_text()}"
            headers = json.loads(self.headers.get_edit_text())
            data = json.loads(f"{self.data.get_edit_text()}")
            response = requests.post(url, headers=headers, json=data)
            output = response.json()
        except Exception as e:
            output = f"Error: {e}, code"
        
        self.response_output.set_text(f"Response:\n" + json.dumps(output, indent=2))
