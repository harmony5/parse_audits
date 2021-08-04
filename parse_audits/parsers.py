import json
from typing import Any, Dict, Generator

from parse_audits.models import ENTRY_PATTERN, FIELD_PATTERN
from parse_audits.utils import _format_time_string


DictIter = Generator[Dict[Any, Any], None, None]


def _parse_fields_from_text(text: str) -> DictIter:
    """Parse the fields from text to a list of dicts"""
    fields = [field_match.groupdict("") for field_match in FIELD_PATTERN.finditer(text)]

    return fields


def _parse_entries_from_text(text: str) -> DictIter:
    """
    Parse the given AuditTrail text and return a list of audit entries.
    """
    for entry_match in ENTRY_PATTERN.finditer(text):
        # Get the entry
        entry = entry_match.groupdict("")

        entry.update(
            {
                "time": _format_time_string(entry["time"]),
                "user_groups": entry["user_groups"].split(),
                "fields": _parse_fields_from_text(entry["fields"]),
            }
        )

        yield entry


def parse_text_as_json(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a JSON string."""
    return json.dumps(list(_parse_entries_from_text(audit_text)), ensure_ascii=False)


def parse_text_as_csv(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a CSV string."""
    csv_lines = [
        "'time'|'schema'|'user_name'|'user_login'|'user_groups'|\
        'action'|'state'|'field_name'|'delta'|'old'|'new'"
    ]

    for entry in _parse_entries_from_text(audit_text):
        fields = entry["fields"]

        for field in fields:
            csv_lines.append(
                "|".join(
                    [
                        entry["time"],
                        entry["schema"],
                        entry["user_name"],
                        entry["user_login"],
                        entry["user_groups"],
                        entry["action"],
                        entry["state"],
                        field["field_name"],
                        field["delta"],
                        field["old"],
                        field["new"],
                    ]
                )
            )

    return "\n".join(csv_lines)


def parse_text_as_excel(audit_text: str) -> bytes:
    """Parse the given AuditTrail text and return an Excel spreadsheet."""
    raise NotImplementedError()
