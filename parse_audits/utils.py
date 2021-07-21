def _read_file(filename, mode="r"):
    with open(filename, mode, encoding="utf-8") as f:
        return f.read()


def _write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def _format_time_string(time_string: str) -> str:
    """Format a time string to a more standard format."""
    
    # Remove the ':' from the timezone offset part
    index = time_string.rfind(":")
    return time_string[:index] + time_string[index + 1 :]
