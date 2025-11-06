import io
import logging
from contextlib import contextmanager
from logging import LogRecord
from typing import Generator, List, Type, Union

from rich.console import Console, ConsoleRenderable
from rich.logging import RichHandler
from rich.text import Text

LOG_FILENAME = "routine_output.log"
LOG_LEVEL = logging.INFO
CONSOLE = Console()

GRAY = "\x1b[38;21m"
WHITE = "\x1b[38;5;15m"
YELLOW = "\x1b[38;5;226m"
RED = "\x1b[38;5;196m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"


def capture_rich_renderable_as_string(renderable) -> str:
    string_io = io.StringIO()
    capture_console = Console(file=string_io, record=True, width=200)
    capture_console.print(renderable)
    return string_io.getvalue()


class NoFileOnlyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not getattr(record, 'file_only', False)


class CustomRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_message(self, record: LogRecord, message: str) -> ConsoleRenderable:
        message_renderable = super().render_message(record, message)
        return Text.assemble(
            Text(f"{record.name} ", style="bold cyan"),
            message_renderable,
        )


class _DuplicateFilter:
    def __init__(self) -> None:
        self.msgs = set()

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg in self.msgs:
            return False
        self.msgs.add(record.msg)
        return True


def setup_logging(
    output_file: Union[str, None] = None,
    logger: logging.Logger = logging.getLogger(""),
    level: Union[int, None] = logging.INFO,
) -> logging.Logger:
    if output_file is None:
        output_file = LOG_FILENAME
    if level is None:
        level = LOG_LEVEL

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    console_handler = CustomRichHandler(
        console=CONSOLE,
        rich_tracebacks=True,
        show_time=True,
        show_level=True,
        show_path=True,
        log_time_format="[%Y-%m-%d %H:%M:%S]",
    )
    console_handler.addFilter(NoFileOnlyFilter())
    logger.addHandler(console_handler)

    log_file = open(output_file, "a")
    file_console = Console(file=log_file, record=True, width=200)
    file_handler = CustomRichHandler(
        console=file_console,
        show_time=True,
        show_level=True,
        show_path=True,
        log_time_format="[%Y-%m-%d %H:%M:%S.%f]",
        rich_tracebacks=False,
        markup=False,
    )
    logger.addHandler(file_handler)

    # Install the duplicate filter permanently if not already present.
    if not any(isinstance(f, _DuplicateFilter) for f in logger.filters):
        logger.addFilter(_DuplicateFilter())

    return logger


class LogContext:

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    @contextmanager
    def suppress_console_logging(self) -> Generator[None, None, None]:
        original_handlers = list(self.logger.handlers)  # Make a copy
        console_handlers_to_remove: List[logging.Handler] = []

        for handler in original_handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                console_handlers_to_remove.append(handler)
                self.logger.removeHandler(handler)

        try:
            yield
        finally:
            for handler in console_handlers_to_remove:
                if handler not in self.logger.handlers:  # Avoid adding duplicates if somehow re-added
                    self.logger.addHandler(handler)

            current_handlers = list(self.logger.handlers)
            for handler in original_handlers:
                if handler not in current_handlers and handler not in console_handlers_to_remove:
                    self.logger.addHandler(handler)

    @contextmanager
    def duplicate_filter(self) -> Generator[None, None, None]:
        if any(isinstance(f, _DuplicateFilter) for f in self.logger.filters):
            yield
        else:
            dup_filter = _DuplicateFilter()
            self.logger.addFilter(dup_filter)
            try:
                yield
            finally:
                self.logger.removeFilter(dup_filter)

    @contextmanager
    def logging_raised_Error(self) -> Generator[None, None, None]:
        try:
            yield
        except Exception as e:
            self.logger.error(e)
            raise

    @contextmanager
    def set_logging_level(self, level: int) -> Generator[None, None, None]:
        _old_level = self.logger.level
        self.logger.setLevel(level)
        try:
            yield
        finally:
            self.logger.setLevel(_old_level)

    @contextmanager
    def suppress_logging(self) -> Generator[None, None, None]:
        original_level = self.logger.level
        self.logger.setLevel(logging.CRITICAL + 1)
        try:
            yield
        finally:
            self.logger.setLevel(original_level)

    @contextmanager
    def log_and_suppress(self, *exceptions: Type[Exception], msg: str = "An exception was suppressed"):
        try:
            yield
        except exceptions or (Exception,) as e:
            self.logger.error(f"{msg}: {type(e).__name__} - {e}", exc_info=True)