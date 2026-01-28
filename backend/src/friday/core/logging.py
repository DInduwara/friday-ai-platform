from __future__ import annotations

import logging
import sys

from friday.core.config import settings


def configure_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quieter 3rd party logs by default
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
