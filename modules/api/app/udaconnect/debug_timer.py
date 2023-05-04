from contextlib import contextmanager
import logging
from typing import Generator

import datetime as dt

logger = logging.getLogger("udaconnect-api")


@contextmanager
def logged_timer(action_message: str) -> Generator[None, None, None]:
    started_at = dt.datetime.now()
    yield
    finished_at = dt.datetime.now()
    logger.debug(f"{action_message} took {finished_at - started_at}.")
