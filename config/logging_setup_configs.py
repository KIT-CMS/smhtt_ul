import logging
import shutil
import textwrap
from contextlib import contextmanager
from typing import Generator, Union


__LOG_FILENAME__ = "routine_output.log"
__LOG_LEVEL__ = logging.INFO

GRAY = "\x1b[38;21m"
WHITE = "\x1b[38;5;15m"
YELLOW = "\x1b[38;5;226m"
RED = "\x1b[38;5;196m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""
    def __init__(self, use_color: bool = True) -> None:
        super().__init__()
        self.use_color = use_color
        self.FORMATS = {
            logging.DEBUG: lambda fmt: f"{GRAY}{fmt}{RESET}" if use_color else fmt,
            logging.INFO: lambda fmt: f"{WHITE}{fmt}{RESET}" if use_color else fmt,
            logging.WARNING: lambda fmt: f"{YELLOW}{fmt}{RESET}" if use_color else fmt,
            logging.ERROR: lambda fmt: f"{RED}{fmt}{RESET}" if use_color else fmt,
            logging.CRITICAL: lambda fmt: f"{BOLD_RED}{fmt}{RESET}" if use_color else fmt,
        }

    def format(self, record: logging.LogRecord) -> str:
        # Build the fixed parts.
        asctime = self.formatTime(record)
        left_part = f"{asctime} | {record.name} | "
        right_part = f" {record.filename}: L{record.lineno:4d}"
        mid_prefix = f"{record.levelname}: "

        try:  # Determine terminal width (default to 80 columns).
            term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
        except Exception:
            term_width = 80

        # Compute lengths.
        left_len = len(left_part)
        right_len = len(right_part)
        level_len = len(mid_prefix)
        avail_mid = max(10, term_width - left_len - level_len - right_len)

        raw_message = record.getMessage()
        # Check if the message already contains newlines.
        if "\n" in raw_message:
            raw_lines = raw_message.split("\n")
            # Process the first line specially.
            if len(raw_lines[0]) <= avail_mid:
                first_line_text = raw_lines[0]
                pad_first = avail_mid - len(first_line_text)
                line1 = f"{left_part}{mid_prefix}{first_line_text}{' ' * pad_first}{right_part}"
            else:
                # If the first segment is too long, wrap it.
                wrapped_first = textwrap.wrap(raw_lines[0], width=avail_mid)
                first_line_text = wrapped_first[0]
                pad_first = avail_mid - len(first_line_text)
                line1 = f"{left_part}{mid_prefix}{first_line_text}{' ' * pad_first}{right_part}"
                # Prepend any leftover from wrapping the first line.
                indent = " " * (left_len + level_len)
                rest_first = []
                for line in wrapped_first[1:]:
                    pad = avail_mid - len(line)
                    rest_first.append(f"{indent}{line}{' ' * pad}")
            # For subsequent lines, we now prepend left_len padding.
            subsequent_lines = []
            if "\n" in raw_message:
                # If we wrapped the first line, add the wrapped leftovers.
                if len(raw_lines[0]) > avail_mid and wrapped_first[1:]:
                    subsequent_lines.extend(rest_first)
                # Then for any remaining original lines, add left_part padding.
                for line in raw_lines[1:]:
                    subsequent_lines.append(" " * left_len + line)
            formatted = "\n".join([line1] + subsequent_lines)
        else:
            # Default handling: wrap the message automatically.
            wrapped = textwrap.wrap(raw_message, width=avail_mid)
            if not wrapped:
                wrapped = [""]
            first_line_text = wrapped[0]
            pad_first = avail_mid - len(first_line_text)
            line1 = f"{left_part}{mid_prefix}{first_line_text}{' ' * pad_first}{right_part}"
            indent = " " * (left_len + level_len)
            subsequent_lines = []
            for line in wrapped[1:]:
                pad = avail_mid - len(line)
                subsequent_lines.append(f"{indent}{line}{' ' * pad}")
            formatted = "\n".join([line1] + subsequent_lines)

        # Append a horizontal separator line at the end.
        formatted += f"\n{'-' * term_width}"
        return self.FORMATS[record.levelno](formatted) if self.use_color else formatted


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
        output_file = __LOG_FILENAME__
    if level is None:
        level = __LOG_LEVEL__

    logger.setLevel(level)

    console_formatter = CustomFormatter(use_color=True)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_formatter = CustomFormatter(use_color=False)
    file_handler = logging.FileHandler(output_file, "a")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Install the duplicate filter permanently if not already present.
    if not any(isinstance(f, _DuplicateFilter) for f in logger.filters):
        logger.addFilter(_DuplicateFilter())

    return logger


class LogContext:
    
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
    
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
        original_level = self.logger.level
        self.logger.setLevel(level)
        try:
            yield
        finally:
            self.logger.setLevel(original_level)

    @contextmanager
    def suppress_logging(self) -> Generator[None, None, None]:
        original_level = self.logger.level
        self.logger.setLevel(logging.CRITICAL + 1)
        try:
            yield
        finally:
            self.logger.setLevel(original_level)
