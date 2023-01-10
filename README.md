# MyTaktlausvev

**MyTaktlausvev** is a fork of [Taktlausveven](https://gitlab.com/taktlause/taktlausveven/), which aims to make it super-simple for anyone to make their own orchestra website based on Taktlausveven. All possibly orchestra-specific details are made generic and can be changed in [`config.toml`](config.toml).

## Installation

Requires Python 3

```
$ git submodule update --init --recursive
$ pip install -r requirements.txt
```

## Usage

```
$ python3 build_website.py [--clean] [-f CONFIG_FILE]
```

`build_website.py` copies everything from [`webiste_source`](website_source/) into [`website_build`](website_build/) and everything from [`static_files`](static_files/) into [`website_build/site/static/`](website_build/site/static/). Then it goes through all files ending with `.py`, `.html`, `.scss` and `.js` and replaces every occurrance of `(MYTAKTLAUSVEV_VARIABLE(category.variable))` with the value of `category.variable` in the specified config file (defaults to [`config.toml`](config.toml)).

## Config options

### About variable types

Each config option has one of the following variable types:

- **Visible text** is a very easy-to-understand variable type. The text is visible to the user in some specific contexts. In other words, the required format is a human-readable string.
- **Color code** should be the hex code for a color, e.g. `#FF0000`.
- **Static file path** should be the relative path to a file in the [`static_files`](static_files/), relative to the [`static_files`](static_files/) directory itself. It can also be a static file path to one of the static files in the website source code.
- **Context dependent** A piece of text to be used in a specific context. Use common sense, e.g. avoid æøå and other special characters when they are not appropriate.

### Full config options reference

| Option                             | Variable type         | Description                                                                     |
| ---------------------------------- | --------------------- | ------------------------------------------------------------------------------- |
| `appearance.base_page_title`       | **Visible text**      | Base for page title shown in browser tab.                                       |
| `appearance.primary_color`         | **Color code**        | Primary color on entire site.                                                   |
| `appearance.icon`                  | **Static file path**  | Icon shown in browser tab.                                                      |
| `appearance.navbar.logo`           | **Static file path**  | Logo shown in navbar.                                                           |
| `appearance.navbar.logo_santa_hat` | **Static file path**  | Logo shown in navbar in December.                                               |
| `appearance.navbar.title`          | **Visible text**      | Full title shown in navbar (recommended maximum 32 characters)                  |
| `appearance.navbar.title_short`    | **Visible text**      | Short version of title shown in navbar (recommended maximum 16 characters).     |
| `initial_data.orchestra_name`      | **Visible text**      | Name of student orchestra used in initial data generation.                      |
| `initial_data.superuser.username`  | **Context dependent** | Username for superuser.                                                         |
| `initial_data.superuser.email`     | **Context dependent** | Email for superuser.                                                            |
| `initial_data.superuser.password`  | **Context dependent** | Password for superuser.                                                         |
| `initial_data.site.domain`         | **Context dependent** | Domain for site.                                                                |
| `production.hosting_solution`      | **Context dependent** | The production hosting solution to use. Must be either `"azure"` or `"server"`. |
| `readme.project_title`             | **Visible text**      | Project title used in `README.md`.                                              |
| `readme.orchestra_name`            | **Visible text**      | Name of student orchestra used in `README.md`.                                  |
