import tomli
from pathlib import Path
from primary2024_dashboard.logger import Logger


def read_toml_file(file_path: Path) -> dict:
    logger = Logger('func:read_toml_file')
    if isinstance(file_path, str):
        file_path = Path(file_path)
        logger.info(f"Converted file_path to Path object: {file_path.name}")
    with open(file_path, "rb") as file:
        logger.info(f"Opened file: {file_path.name}")
        return tomli.load(file)
