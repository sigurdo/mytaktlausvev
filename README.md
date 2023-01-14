# MyTaktlausvev

**MyTaktlausvev** is a framework for making a custom website for a student orchestra built around it's own [fork](./website_source) of [Taktlausveven](https://gitlab.com/taktlause/taktlausveven/), which aims to make it super-simple for anyone to make their own student orchestra website based on Taktlausveven.

Orchestra-specific details are made generic and configurable from [TOML](https://toml.io/en/) files.

## Installation

Requires Python 3 and Docker (with docker compose).

```
git submodule update --init --recursive
python3 -m pip install -r requirements.txt
```

## Setup

```
./wizard.py
```

## Usage

`build_website.py` copies everything from [`webiste_source`](website_source/) into [`website_build`](website_build/) and everything from [`static_files`](static_files/) into [`website_build/site/static/`](website_build/site/static/). Then it goes through all source code files, and replaces every occurrance of `(MYTAKTLAUSVEV_VARIABLE(config_variable))` with the value of `config_variable` in the specified config. The config is obtained form merging TOML config files.

### Command line interface

```
./build_website.py [-h] [-b base_config_file] [-s server_secrets_file] [--clean] [main_config_file]
```

| Parameter             | Default value                                | Description                                           |
| --------------------- | -------------------------------------------- | ----------------------------------------------------- |
| `base_config_file`    | [`taktlausconfig.toml`](taktlausconfig.toml) | Base config file (lowest priority)                    |
| `server_secrets_file` | [`server_secrets.toml](server_secrets.toml)  | Server secrets file (highest priority)                |
| `main_config_file`    | `config.toml`                                | Main config file (medium priority)                    |
| `clean`               | Flag, is by default not given                | Deletes everything in `website_build` before building |

### Python interface

```py
def build_website(config_files, clean=False)
```

| Argument       | Description                                                       |
| -------------- | ----------------------------------------------------------------- |
| `config_files` | List of config file paths. The later entries take higher priority |
| `clean`        | Deletes everything in `website_build` before building             |


## Config variables

### About variable types

Each config variable has one of the following variable types:

- **Visible text** is a very easy-to-understand variable type. The text is visible to the user in some specific contexts. In other words, the required format is a human-readable string.
- **Color code** should be the [HTML color code](https://html-color.codes/), preferably a hex code for a color, e.g. `#ff0000`.
- **Static file path** should be the relative path to a file in the [`static_files`](static_files/), relative to the [`static_files`](static_files/) directory itself. It can also be a static file path to one of the static files in the website source code.
- **Context dependent** A piece of text to be used in a specific context. Use common sense, e.g. avoid æøå and other special characters when they are not appropriate.

### Full config variable reference

| Variable                                             | Variable type         | Description                                                                     |
| ---------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------- |
| `domain`                                             | **Context dependent** | Domain for website.                                                             |
| `appearance.orchestra_name`                          | **Visible text**      | Name of student orchestra.                                                      |
| `appearance.orchestra_name_short`                    | **Visible text**      | Short version of name of student orchestra.                                     |
| `appearance.base_page_title`                         | **Visible text**      | Base for page title shown in browser tab.                                       |
| `appearance.primary_color`                           | **Color code**        | Primary color on entire site.                                                   |
| `appearance.favicon`                                 | **Static file path**  | Favicon shown in browser tab.                                                   |
| `appearance.navbar.logo`                             | **Static file path**  | Logo shown in navbar.                                                           |
| `appearance.navbar.logo_santa_hat`                   | **Static file path**  | Logo shown in navbar in December.                                               |
| `appearance.navbar.title`                            | **Visible text**      | Full title shown in navbar (recommended maximum 32 characters)                  |
| `appearance.navbar.title_short`                      | **Visible text**      | Short version of title shown in navbar (recommended maximum 16 characters).     |
| `appearance.navbar.development_background_color`     | **Visible text**      | Background color of navbar when `PRODUCTION` is `0`.                            |
| `appearance.accounts.orchestra_stuff_fieldset`       | **Visible text**      | Description of fieldset for orchestra related stuff when editing an account.    |
| `appearance.accounts.image_sharing_consent.question` | **Visible text**      | Question used to ask user for image sharing consent.                            |
| `appearance.advent_calendar.title`                   | **Visible text**      | Title of advent calendar.                                                       |
| `appearance.events.feed.filename`                    | **Context dependent** | Filename to use for calendar feed.                                              |
| `appearance.events.feed.title`                       | **Visible text**      | Title to use for calendar feed.                                                 |
| `appearance.events.feed.description`                 | **Visible text**      | Description to use for calendar feed.                                           |
| `appearance.manifest.name`                           | **Visible text**      | App name to use for PWA manifest.                                               |
| `appearance.manifest.short_name`                     | **Visible text**      | Short app name to use for PWA manifest.                                         |
| `appearance.manifest.description`                    | **Visible text**      | App description to use for PWA manifest.                                        |
| `appearance.manifest.background_color`               | **Color code**        | Background color to use for PWA manifest.                                       |
| `appearance.manifest.theme_color`                    | **Color code**        | Theme color to use for PWA manifest.                                            |
| `appearance.manifest.apple_touch_icon`               | **Static file path**  | Apple touch icon to use for PWA manifest.                                       |
| `initial_data.superuser.username`                    | **Context dependent** | Username for superuser.                                                         |
| `initial_data.superuser.email`                       | **Context dependent** | Email for superuser.                                                            |
| `initial_data.superuser.password`                    | **Context dependent** | Password for superuser.                                                         |
| `readme.project_title`                               | **Visible text**      | Project title used in `README.md`.                                              |
| `readme.orchestra_name`                              | **Visible text**      | Name of student orchestra used in `README.md`.                                  |
| `production.hosting_solution`                        | **Context dependent** | The production hosting solution to use. Must be either `"azure"` or `"server"`. |
| `production.server.nginx.http_server_name`           | **Context dependent** | Space separated list of domains for the NGINX HTTP server                       |
| `production.server.nginx.https_server_name`          | **Context dependent** | Space separated list of domains for the NGINX HTTPS server                      |
| `production.server.nginx.website_name`               | **Context dependent** | Name of the website used by Certbot                                             |
| `production.server.environment.certbot_email`        | **Context dependent** | Email used by Certbot to send notification about security issues.               |
| `production.server.environment.database_password`    | **Context dependent** | Database password.                                                              |
| `production.server.environment.allowed_hosts`        | **Context dependent** | Value of Django `settings.ALLOWED_HOSTS`.                                       |
| `production.server.environment.csrf_trusted_origins` | **Context dependent** | Value of Django `settings.CSRF_TRUSTED_ORIGINS`.                                |
