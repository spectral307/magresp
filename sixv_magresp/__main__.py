from json import load as load_json
from rich import print as print_rich
import importlib.resources


def get_config():
    with importlib.resources.open_text(__package__, "config.json") as file:
        return load_json(file)


def main():
    config = get_config()
    print_rich(config)


if __name__ == "__main__":
    main()
