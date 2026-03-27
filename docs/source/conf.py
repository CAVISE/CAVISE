import os

# Configuration file for the Sphinx documentation builder.

project = "CAVISE"
copyright = "2024, CAVISE Dev Team"
author = "CAVISE Dev Team"
release = "1.0"

html_logo = "_static/images/Logo.svg"

extensions = []

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "cavise"
html_theme_path = [os.path.abspath("./_theme")]
html_static_path = ["_static"]
html_js_files = ["js/cavise-theme.js"]
html_permalinks = False
html_context = {
    "github_repo_name": "CAVISE/CAVISE",
    "github_repo_url": "https://github.com/CAVISE/CAVISE",
    "github_repo_api": "https://api.github.com/repos/CAVISE/CAVISE",
}

html_theme_options = {
    "logo_only": True,
    "collapse_navigation": False,
    "navigation_depth": 4,
    "style_external_links": True,
    "style_nav_header_background": "#0c1224",
    "sticky_navigation": True,
}
