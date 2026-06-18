import sys
import json
from pathlib import Path
from loguru import logger
from app.config.settings import settings


def serialize(record: dict) -> str:
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "context": {
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            **record["extra"],
        },
    }
    return json.dumps(subset)


def patching(record: dict) -> None:
    record["extra"]["serialized"] = serialize(record)


def setup_logging() -> None:
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        format="{extra[serialized]}",
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    logger.add(
        settings.LOG_FILE,
        format="{extra[serialized]}",
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    logger.configure(patcher=patching)


def get_logger(name: str):
    return logger.bind(logger_name=name)
