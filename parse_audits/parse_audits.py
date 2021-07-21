from typing import Generator, List, Dict, Any
import json

import regex as re

from .models import ENTRY_PATTERN, FIELD_PATTERN
from .utils import _format_time_string



def parse_audit_fields_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse the fields from text to a list of dicts"""
    fields = [
        {
            "field_name": field_name,
            "delta": delta,
            "old": old.strip() if old else "",
            "new": new.strip() if new else "",
        }
        for field_name, delta, old, new in FIELD_PATTERN.findall(text)
    ]

    return fields


def parse_audit_entries_from_text(audit_text: str) -> Generator[Dict[str, Any], None, None]:
    """
    Parse the given AuditTrail text and return a list of audit entries.
    """
    for entry_match in ENTRY_PATTERN.finditer(audit_text):
        # Get the entry
        entry = entry_match.groupdict()

        entry.update(
            {
                "time": _format_time_string(entry["time"]),
                "user_groups": entry["user_groups"].split(),
                "fields": parse_audit_fields_from_text(entry["fields"]),
            }
        )

        yield entry


def parse_audit_text_as_json(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a JSON string."""
    return json.dumps(list(parse_audit_entries_from_text(audit_text)), ensure_ascii=False)


def parse_audit_text_as_csv(audit_text: str) -> str:
    """Parse the given AuditTrail text and return a CSV string."""
    csv_lines = [
        "'time'|'schema'|'user_name'|'user_login'|'user_groups'|\
        'action'|'state'|'field_name'|'delta'|'old'|'new'"
    ]

    for entry in parse_audit_entries_from_text(audit_text):
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


def parse_audit_text_as_excel(audit_text: str):
    """Parse the given AuditTrail text and return an Excel spreadsheet."""
    raise NotImplementedError()
