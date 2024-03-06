import tomli
from pathlib import Path
from primary2024_dashboard.logger import Logger


class TomlReader:
    """
    Reads a TOML file and sets the key-value pairs as attributes of the class.
    The key-value pairs are accessible as attributes of the class.

    :param file_path: Path to the TOML file
    :type file_path: Path or str
    """

    def __init__(self, file_path):
        self.data = read_toml_file(file_path)

    def __call__(self, *args, **kwargs):
        return self.data


def read_toml_file(file_path: Path) -> dict:
    logger = Logger('func:read_toml_file')
    if isinstance(file_path, str):
        file_path = Path(file_path)
        logger.info(f"Converted file_path to Path object: {file_path.name}")
    with open(file_path, "rb") as file:
        logger.info(f"Opened file: {file_path.name}")
        return tomli.load(file)
