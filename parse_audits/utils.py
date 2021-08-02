import re
from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd


def _read_file(filename: str, binary: bool = False) -> str:
    """Read a file and return its content."""
    if binary:
        mode = "rb"
        encoding = None
    else:
        mode = "r"
        encoding = "utf-8"

    with open(filename, mode, encoding="utf-8") as f:
        return f.read()


def _write_file(filename: str, content: str, *, binary: bool = False) -> int:
    """Write a file with the given content."""
    if binary:
        mode = "wb"
        encoding = None
    else:
        mode = "w"
        encoding = "utf-8"

    with open(filename, mode, encoding=encoding) as f:
        return f.write(content)


def _format_time_string(time_string: str) -> str:
    """Format a time string.

    Converts from:  'YYYY-MM-DD HH:mm:SS ±HH:mm'
    To:             'YYYY-MM-DD HH:mm:SS ±HHmm' (Remove the ':' from the timezone offset part)

    So it can be easily parsed by the datetime module using the string:
    '%Y-%m-%d %H:%M:%S %z'
    """
    time_pattern = r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d\d):(\d\d)$"
    return re.sub(time_pattern, r"\1\2", time_string)


def _filter_dict_by_keys(
    dictionary: Dict[Any, Any],
    *,
    keys: Optional[List[Any]] = None,
    exclude: Optional[List[str]] = None
) -> dict:
    """Filter a dictionary to only include the given keys."""
    if keys is None and exclude is None:
        return dictionary
    elif keys is None:
        return {k: v for k, v in dictionary.items() if k not in exclude}
    elif exclude is None:
        return {k: v for k, v in dictionary.items() if k in keys}
    else:
        keys = set(keys) - set(exclude)
        return {k: v for k, v in dictionary.items() if k in keys}


def _convert_dicts_to_csv(
    dicts: List[Dict[Any, Any]],
    *,
    include_keys: Optional[List[str]] = None,
    exclude_keys: Optional[List[str]] = None,
    delimiter: str = ",",
    **kwargs
) -> str:
    """Convert a list of dictionaries to a CSV string.

    :param dicts: The dictionaries to convert.
    :param include_keys: The keys to include in the CSV. Can also rearange the order of the keys.
    :param exclude_keys: The keys to exclude from the CSV.
    :param delimiter: The delimiter to use.
    :param kwargs: Additional arguments to pass to pandas.DataFrame.to_csv when converting to csv.
    """
    df = pd.DataFrame.from_records(
        dicts,
        columns=include_keys,
        exclude=exclude_keys,
    )

    with StringIO() as output_csv:
        df.to_csv(
            output_csv,
            sep=delimiter,
            header=True,
            index=False,
            line_terminator="\n",
            **kwargs
        )
        return output_csv.getvalue()
