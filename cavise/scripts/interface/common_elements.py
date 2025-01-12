import os
import urwid as u


class CommonElements:
    def update_file_list(self):
        """Updates the list of files in the './dc-configs' directory.

        Sets the text of the file_list widget to display available files or an error message.
        """
        try:
            self.files = os.listdir('./dc-configs')
            formatted_files = "\n".join(self.files)
        except FileNotFoundError:
            formatted_files = "Directory './dc-configs' not found."
        self.file_list.set_text("Available files:\n" + formatted_files)

    def create_scrollable_script_output(self, script_output):
        """Creates a scrollable area for displaying script output.

        Returns:
            u.Filler: A Filler widget that holds the scrollable script output.
        """
        listbox_content = u.ListBox([u.Text("")])
        listbox_content.body.append(script_output)

        scrollable_output = u.BoxAdapter(listbox_content, height=50) 
        return u.Filler(scrollable_output, valign='top')