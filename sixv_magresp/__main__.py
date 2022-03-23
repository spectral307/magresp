from json import load as load_json
from rich import print as print_rich
import importlib.resources
import pandas as pd
from gtrfile import GtrFile
from os.path import join


def get_config():
    with importlib.resources.open_text(__package__, "config.json") as file:
        return load_json(file)


def main():
    config = get_config()

    record_path = join(config["input"]["dir"], config["input"]["file"])

    gtr = GtrFile(record_path)


if __name__ == "__main__":
    main()
