from dataclasses import dataclass
from typing import List, Dict, Any

from regex import compile as regex_compile


ENTRY_PATTERN = regex_compile(
    r"""(?sx)
        ====START====[\r\n]+
        [^:]+:\s+ (?P<time>        [^\r\n]*)[\r\n]+
        [^:]+:\s+ (?P<schema>      [^\r\n]*)[\r\n]+
        [^:]+:\s+ (?P<user_name>   [^\r\n]+)[\r\n]+
        [^:]+:\s+ (?P<user_login>  [^\r\n]+)[\r\n]+
        [^:]+:\s+ (?P<user_groups> [^\r\n]*)[\r\n]+
        [^:]+:\s+ (?P<action>      [^\r\n]+)[\r\n]+
        [^:]+:\s+ (?P<state>       [^\r\n]*)[\r\n]+
        ==Fields==[\r\n]+
        (?P<fields>.+?)
        [\r\n]+
        ====END====
    """
)

FIELD_PATTERN = regex_compile(
    r"""(?sx)
        ((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
        (?: Old \s+: [\t\f ]+ (?P<old>.*?) [\r\n]+
        \s+ New \s+: \s+)?    (?P<new>.+?)
        (?=[\r\n]+(?1)\S|$)
    """
)


@dataclass
class AuditEntryField:
    """Represents a single field in an AuditTrail entry."""
    field_name: str
    delta: str
    old: str
    new: str


@dataclass
class AuditEntry:
    """Represents a single AuditTrail entry."""
    time: str
    schema: str
    user_name: str
    user_login: str
    user_groups: List[str]
    action: str
    state: str
    fields: List[Dict[str, Any]]

