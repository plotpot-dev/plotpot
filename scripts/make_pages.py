import json
import os
from typing import Any

from jinja2 import Environment, FileSystemLoader

DATA_DIR = "data"
TEMPLATES_DIR = "templates"
STATIC_DIR = "pages"

tokens_data_path = os.path.join(DATA_DIR, "tokens.json")
index_template_path = os.path.join(TEMPLATES_DIR, "index.html.jinja")
token_template_path = os.path.join(TEMPLATES_DIR, "token.html.jinja")
index_page_path = os.path.join(STATIC_DIR, "index.html")


def token_page_path(ticker: str) -> str:
    return os.path.join(STATIC_DIR, f"{ticker}.html")


# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def read_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_html_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def generate_html_files() -> None:
    tokens = read_json_file(tokens_data_path)
    token_template = env.get_template(os.path.basename(token_template_path))
    index_template = env.get_template(os.path.basename(index_template_path))

    # Generate individual token pages
    for token in tokens:
        token_html = token_template.render(token)
        write_html_file(token_page_path(token["ticker"]), token_html)
        print(f"HTML file {token["ticker"]}.html has been generated.")

    # Generate index page
    index_html = index_template.render(tokens=tokens)
    write_html_file(index_page_path, index_html)
    print("HTML file index.html has been generated.")


if __name__ == "__main__":
    generate_html_files()
