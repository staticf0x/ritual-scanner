import json
import sys

from devtools import debug
from loguru import logger

from ritual_scanner.scanner.scanner import Scanner

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level:7s}</level> | {message}",
    level="DEBUG",
    colorize=True,
)

scanner = Scanner()
scanner.scan()

with open("items.json", "w") as f:
    json.dump(
        {"items": [it.model_dump() for it in scanner.items]},
        f,
        indent=4,
    )
