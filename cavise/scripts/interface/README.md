#Adding New Functionality:

0. The entire functionality of the tool must be wrapped in Docker.
1. Add a file for the tool in the directory CAVISE-HOME/cavise/scripts/interface with the name \<tool-name>_view.py.
2. In this file, implement the functionality you deem necessary for your interface. Everything is written using the urwid library. The library has plenty of documentation, examples, and templates, so it will be easy to understand.
3. In the file CAVISE-HOME/interface.py, import your module.

```python
from cavise.scripts.interface.<tool-name>_view import ToolNameView
```

4. In the App class, add your tool to the self.menu_top section, similar to the other menu items, just before "About Us":

```python
self.menu_top = self.menu(
    "Main Menu",
    [
        self.menu_button("Info", self.show_info),
        self.sub_menu(
            "Admin Panel",
            [
                self.menu_button("Simulator control panel", self.show_cavise),
                self.menu_button("OpenCDA", self.item_chosen),
                self.menu_button("Artery", self.item_chosen),
                self.menu_button("Carla", self.item_chosen),
            ],
        ),
        self.menu_button("Generate compose configs", self.show_compose_gen),
        self.menu_button("Scenario Manager", self.show_scenario_manager),
        self.menu_button("<tool-name>", self.show_<tool-name>),
        self.menu_button("About Us", self.show_aboutus),
    ],
)
```

5. In the App class, implement the show_\<tool-name> method, for example:

```python
def show_info(self, button: u.Button) -> None:
    """Shows the Info view when the 'Info' button is pressed.
    
    Args:
        button (u.Button): The button that triggered the event.
    """
    status_view = InfoView()
    status_view.update_statuses()
    self.top.update_card(u.Filler(u.Pile([('weight', 10, status_view)]), valign="top"))
```

6. Create a Merge Request for your changes. The rules for working with GitLab can be found on the project's Notion page.

