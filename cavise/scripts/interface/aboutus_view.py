import os
import subprocess
import urwid as u
import textwrap


class AboutUsView(u.WidgetWrap):
    """View for displaying information about the application, including logo and details.

    Displays the application logo, version, and a link to the GitHub repository.
    The logo and text are aligned and presented in a user-friendly layout.
    """

    def __init__(self):
        """Initializes the AboutUsView with the logo, version, and GitHub link."""
        self.banner = textwrap.dedent("""                                                                                             
         ██████╗     █████╗     ██╗   ██╗    ██╗    ███████╗    ███████╗ 
        ██╔════╝    ██╔══██╗    ██║   ██║    ██║    ██╔════╝    ██╔════╝
        ██║         ███████║    ██║   ██║    ██║    ███████╗    █████╗  
        ██║         ██╔══██║    ╚██╗ ██╔╝    ██║    ╚════██║    ██╔══╝  
        ╚██████╗    ██║  ██║     ╚████╔╝     ██║    ███████║    ███████╗
         ╚═════╝    ╚═╝  ╚═╝      ╚═══╝      ╚═╝    ╚══════╝    ╚══════╝                                                                                 

        Connected & Automated Vehicle Integrated Simulation Environment
        -------------------------------------------         
        | [o] version: 1.0                        |
        | [o] github:  https://github.com/CAVISE  |                              
        -------------------------------------------""")

        self.logo = u.Padding(u.AttrMap(u.Text(self.banner), "logo"), left=5, right=2)
        self.about = u.Text("")

        logo_filler = u.Filler(self.logo, valign='top')
        about_filler = u.Filler(self.about, valign='top')

        pile = u.Pile([
            ('weight', 1, logo_filler),
            ('weight', 1, about_filler),
        ])
        u.WidgetWrap.__init__(self, pile)
