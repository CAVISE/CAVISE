from __future__ import annotations

import os
import urwid as u
import typing
import importlib

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

from cavise.scripts.interface.info_view import InfoView
from cavise.scripts.interface.cavise_view import CAVISEView
from cavise.scripts.interface.compose_gen_view import ComposeGenView
from cavise.scripts.interface.scenario_manager_view import ScenarioManagerView
from cavise.scripts.interface.aboutus_view import AboutUsView
from cavise.scripts.interface.component_view import ComponentView
from cavise.scripts.interface.help_view import HelpView


class MenuCardLayout(u.WidgetPlaceholder):
    """A layout for the menu and card, supporting dynamic updates."""
    
    def __init__(self, menu: u.Widget) -> None:
        """Initializes MenuCardLayout with a given menu and a default card.
        
        Args:
            menu (u.Widget): The menu widget to display.
        """
        self.menu = u.LineBox(menu)
        self.card = u.LineBox(u.Filler(u.Pile([('weight', 10, AboutUsView())]), valign="top"))

        self.body = u.Columns([("weight", 2, self.menu), ("weight", 8, self.card)])
        super().__init__(self.body)
        self.previous_menu = None

    def update_card(self, widget: u.Widget) -> None:
        """Updates the card content with a new widget.
        
        Args:
            widget (u.Widget): The widget to update the card with.
        """
        self.previous_menu = self.menu
        self.card = u.LineBox(widget)
        self.body = u.Columns([("weight", 2, self.menu), ("weight", 8, self.card)])

        self.original_widget = self.body 

    def keypress(self, size: typing.Tuple[int, ...], key: str) -> typing.Optional[str]:
        """Handles keypress events, allowing navigation back to the previous menu.
        
        Args:
            size (tuple): The size of the screen.
            key (str): The key pressed.
        
        Returns:
            str or None: The key to pass along or None to consume the key event.
        """
        if key == 'esc' and self.previous_menu:
            self.body = u.Columns([("weight", 2, self.previous_menu), ("weight", 8, self.card)])
            self.original_widget = self.body
            return None
        elif key == 'q':
            raise u.ExitMainLoop()
        return super().keypress(size, key)


class App:
    """Main application class to manage the menu and views."""
    
    def __init__(self):
        """Initializes the application with the main menu and top layout."""
        self.menu_top = self.menu(
            "Main Menu",
            [
                self.menu_button("System Info", self.show_info),
                self.sub_menu(
                    "Admin Panel",
                    [
                        self.menu_button("Simulator Control Panel", self.show_cavise),
                        self.menu_button("OpenCDA Info", lambda button: self.show_component(service="opencda", button=button)),
                        self.menu_button("Artery Info", lambda button: self.show_component(service="artery", button=button)),
                        self.menu_button("Carla Info", lambda button: self.show_component(service="carla", button=button)),
                        self.menu_button("Scenario Manager Info", lambda button: self.show_component(service="scenario-manager", button=button)),
                    ],
                ),
                self.menu_button("Generate Compose Configs", self.show_compose_gen),
                self.menu_button("Scenario Manager", self.show_scenario_manager),
                self.menu_button("About Us", self.show_aboutus),
                self.menu_button("Help", self.show_help),
                self.menu_button("Exit", self.exit),
            ],
        )

        self.top = MenuCardLayout(self.menu_top)

    def exit(self, button: u.Button):
        raise u.ExitMainLoop()

    def start(self):
        """Starts the application, initializing the main event loop."""
        self.palette = [
            ("menu_selected", "black", "light green"),
            ('logo', 'light green', 'default'),  
        ]
        self.loop = u.MainLoop(self.top, palette=self.palette)
        self.loop.run()

    def show_component(self, service, button: u.Button) -> None:
        """Shows the Opencda view when the 'Opencda' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        component_view = ComponentView(service, self.loop)
        
        self.top.update_card(u.Filler(u.Pile([('weight', 10, component_view)]), valign="top"))


    def show_info(self, button: u.Button) -> None:
        """Shows the Info view when the 'Info' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        status_view = InfoView(self.loop)
        self.top.update_card(u.Filler(u.Pile([('weight', 10, status_view)]), valign="top"))

    def show_cavise(self, button: u.Button) -> None:
        """Shows the CAVISE view when the 'Run simulator' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        cavise_view = CAVISEView(self.loop)
        self.top.update_card(u.Filler(u.Pile([('weight', 10, cavise_view)]), valign="top"))

    def show_compose_gen(self, button: u.Button) -> None:
        """Shows the Compose Gen view when the 'Generate compose configs' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        compose_gen_view = ComposeGenView()
        self.top.update_card(u.Filler(u.Pile([('weight', 10, compose_gen_view)]), valign="top"))
    
    def show_scenario_manager(self, button: u.Button) -> None:
        """Shows the Scenario Manager view when the 'Scenario Manager' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        scenario_manager_view = ScenarioManagerView()
        self.top.update_card(u.Filler(u.Pile([('weight', 10, scenario_manager_view)]), valign="top"))

    def show_aboutus(self, button: u.Button):
        """Shows the About Us view when the 'About Us' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        aboutus_view = AboutUsView()
        self.top.update_card(u.Filler(u.Pile([('weight', 10, aboutus_view)]), valign="top"))

    def show_help(self, button: u.Button):
        """Shows the Help view when the 'Help' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        help_view = HelpView()
        self.top.update_card(u.Filler(u.Pile([('weight', 10, help_view)]), valign="top"))

    def menu_button(self, caption: str | tuple[str, str] | list[str | tuple[str, str]], callback: callable[[u.Button], None]) -> u.AttrMap:
        """Creates a menu button widget.
        
        Args:
            caption (str | tuple[str, str] | list[str | tuple[str, str]]): The button label.
            callback (callable[[u.Button], None]): The callback function to call when the button is pressed.
        
        Returns:
            u.AttrMap: The button wrapped in an attribute map for styling.
        """
        button = u.Button(caption, on_press=callback)
        return u.AttrMap(button, None, focus_map="menu_selected")

    def sub_menu(self, caption: str | tuple[str, str] | list[str | tuple[str, str]], choices: list[u.Widget]) -> u.Widget:
        """Creates a submenu overlay for the given choices.
        
        Args:
            caption (str | tuple[str, str] | list[str | tuple[str, str]]): The title for the submenu.
            choices (list[u.Widget]): The list of widget choices for the submenu.
        
        Returns:
            u.Widget: The menu button for the submenu.
        """
        contents = self.menu(caption, choices)
        def open_menu(button: u.Button) -> None:
            overlay = u.Overlay(
                contents,
                self.top.menu,
                align="center", width=("relative", 100), height=("relative", 100), valign="middle"
            )
            self.top.update_card(overlay)
        return self.menu_button([caption, "..."], open_menu)

    def menu(self, title: str | tuple[str, str] | list[str | tuple[str, str]], choices: list[u.Widget]) -> u.ListBox:
        """Creates a menu widget with the given title and choices.
        
        Args:
            title (str | tuple[str, str] | list[str | tuple[str, str]]): The title of the menu.
            choices (list[u.Widget]): The list of menu choices.
        
        Returns:
            u.ListBox: The menu widget containing the title and choices.
        """
        body = [u.Text(title), u.Divider(), *choices]
        return u.ListBox(u.SimpleFocusListWalker(body))

    def item_chosen(self, button: u.Button) -> None:
        """Handles item selection in the menu and displays a confirmation message.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        response = u.Text(["You chose ", button.label, "\n"])
        done = self.menu_button("Ok", self.exit_program)
        self.top.update_card(u.Filler(u.Pile([response, done])))

    def exit_program(self, button: u.Button) -> None:
        """Exits the application when the 'Ok' button is pressed.
        
        Args:
            button (u.Button): The button that triggered the event.
        """
        raise u.ExitMainLoop()

    def generate_card(self, title: str) -> u.Widget:
        """Generates a card widget with information about the given title.
        
        Args:
            title (str): The title to generate information for.
        
        Returns:
            u.Widget: The generated card widget.
        """
        return u.Text(f"Information about {title}")


if __name__ == '__main__':
    if not os.path.exists('dc-configs'):
        os.makedirs('dc-configs')

    app = App()
    app.start()
