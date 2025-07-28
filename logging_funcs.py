import os

SUPPRESS_PRINTS = False
SUPPRESS_LOGS = False

LOGS_PATH = None

def print_(*args, sep=' ', end='\n'):
    global SUPPRESS_LOGS, LOGS_PATH, SUPPRESS_PRINTS
    """Logs and optionally prints a message."""
    msg = sep.join(str(arg) for arg in args)

    if not SUPPRESS_PRINTS:
        print(msg, end=end)

    if not SUPPRESS_LOGS and LOGS_PATH:
        try:
            with open(LOGS_PATH, 'a', encoding='utf-8') as log_file:
                log_file.write(msg + end)
        except Exception as e:
            print_2(f"(Logging error: {e})")

def print_2(*args, sep=' ', end='\n'):
    global SUPPRESS_LOGS, LOGS_PATH, SUPPRESS_PRINTS
    """Only prints if printing is enabled. No logging."""
    if not SUPPRESS_PRINTS:
        print(*args, sep=sep, end=end)