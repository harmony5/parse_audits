import json
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Any, Dict, Generator, Union

import pandas as pd

from .models import ENTRY_PATTERN, FIELD_PATTERN
from .utils import _convert_dicts_to_csv, _format_time_string


DictIter = Generator[Dict[Any, Any], None, None]


def _parse_fields_from_text(text: str) -> DictIter:
    """Parse the fields from text to an iter of field dicts"""
    for field_match in FIELD_PATTERN.finditer(text):
        yield field_match.groupdict("")


def _parse_entries_from_text(text: str) -> DictIter:
    """Parse the given AuditTrail text to an iter of entry dicts."""
    for entry_id, entry_match in enumerate(ENTRY_PATTERN.finditer(text)):
        entry = entry_match.groupdict("")

        entry.update(
            {
                "entry_id": entry_id,
                "time": _format_time_string(entry["time"]),
                "user_groups": entry["user_groups"].split(),
                "fields": list(_parse_fields_from_text(entry["fields"])),
            }
        )

        yield entry


def parse_text_as_csv(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a CSV string."""
    entries = [
        {
            "entry_id": entry["entry_id"],
            "time": entry["time"],
            "schema": entry["schema"],
            "user_name": entry["user_name"],
            "user_login": entry["user_login"],
            "user_groups": ",".join(entry["user_groups"]),
            "action": entry["action"],
            "state": entry["state"],
            **field,
            "old": field["old"].replace("\n", "\\n"),
            "new": field["new"].replace("\n", "\\n"),
        }
        for entry in _parse_entries_from_text(audit_text)
        for field in entry["fields"]
    ]

    return _convert_dicts_to_csv(
        entries,
        delimiter="|",
    )


def parse_text_as_excel(audit_text: str) -> bytes:
    """Parse the given AuditTrail text and return the result as bytes in Excel format."""
    entries = []
    fields = []
    user_groups = []
    for entry in _parse_entries_from_text(audit_text):
        entries.append(
            {
                **entry,
                "user_groups": ",".join(entry["user_groups"]),
            }
        )
        fields.extend(
            {
                "entry_id": entry["entry_id"],
                "time": entry["time"],
                **field,
                "old": field["old"].replace("\n", "\\n"),
                "new": field["new"].replace("\n", "\\n"),
            }
            for field in entry["fields"]
        )
        for group in entry["user_groups"]:
            row = {
                "user_name": entry["user_name"],
                "user_login": entry["user_login"],
                "group_name": group,
            }
            if row not in user_groups:
                user_groups.append(row)

    entries_df = pd.DataFrame(
        entries,
        columns=[
            "entry_id",
            "time",
            "schema",
            "user_name",
            "user_login",
            "user_groups",
            "action",
            "state",
        ],
    )
    fields_df = pd.DataFrame(fields)
    groups_df = pd.DataFrame(user_groups)

    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer) as writer:
            entries_df.to_excel(writer, sheet_name="Audit Entries", index=False)
            fields_df.to_excel(writer, sheet_name="Audit Fields", index=False)
            groups_df.to_excel(writer, sheet_name="User Groups", index=False)

        return buffer.getvalue()


def parse_text_as_json(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a JSON string."""
    return json.dumps(list(_parse_entries_from_text(audit_text)), ensure_ascii=False)


class Format(str, Enum):
    """Represents the format of the parsed data."""

    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"


@dataclass
class Parser:
    """Parser for AuditTrail text."""

    audit_text: str
    format: Format

    def as_csv(self) -> str:
        """Return the parsed AuditTrail text as CSV."""
        return parse_text_as_csv(self.audit_text)

    def as_excel(self) -> bytes:
        """Return the parsed AuditTrail text as Excel."""
        return parse_text_as_excel(self.audit_text)

    def as_json(self) -> str:
        """Return the parsed AuditTrail text as JSON."""
        return parse_text_as_json(self.audit_text)

    def parse(self) -> Union[bytes, str]:
        """Parse the given AuditTrail text according to the given format and return the result."""
        if self.format == Format.CSV:
            return parse_text_as_csv(self.audit_text)
        elif self.format == Format.EXCEL:
            return parse_text_as_excel(self.audit_text)
        elif self.format == Format.JSON:
            return parse_text_as_json(self.audit_text)
        else:
            raise ValueError(f"Unknown format: {self.format}")
