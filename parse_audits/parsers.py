import json
from typing import Any, Dict, Generator

from parse_audits.models import ENTRY_PATTERN, FIELD_PATTERN
from parse_audits.utils import _convert_dicts_to_csv, _format_time_string


DictIter = Generator[Dict[Any, Any], None, None]


def _parse_fields_from_text(text: str) -> DictIter:
    """Parse the fields from text to an iter of field dicts"""
    for field_match in FIELD_PATTERN.finditer(text):
        yield field_match.groupdict("")


def _parse_entries_from_text(text: str) -> DictIter:
    """Parse the given AuditTrail to an iter of entry dicts."""
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
    """Parse the given AuditTrail text and return an Excel spreadsheet."""
    raise NotImplementedError()


def parse_text_as_json(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a JSON string."""
    return json.dumps(list(_parse_entries_from_text(audit_text)), ensure_ascii=False)
