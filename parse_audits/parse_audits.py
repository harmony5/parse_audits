from typing import List, Dict, Any
import regex as re
import json
from os import path

""" v3.0
(?s)(?x)====START====\v
Time         \s+:\s+ (?P<time>\d{4}-\d\d-\d\d\ \d\d:\d\d:\d\d\ [+-]?\d\d:\d\d)\v
Schema\ Rev  \s+:\s+ (?P<schema>\d+)\v
User\ Name   \s+:\s+ (?P<user_name>[\p{L}\s]+)\v
User\ Login  \s+:\s+ (?P<user_login>[uU]\d+|\w+)\v
User\ Groups \s+:\s+ (?P<user_groups>[\w\s]+)\v
Action       \s+:\s+ (?P<action>[\w\s]+)\v
State        \s+:\s+ (?P<state>[\w\s]*)\v
==Fields==\v
(?P<fields>.+?)\v
====END====
"""
""" v3.5
(?sux)
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

""" Field regex v3.0
# This version makes clear which fields have an 'old' and a 'new' value,
# and which ones just have their current value
(?sx)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)[\r\n]+
(?:
    \s+Old \s+: (?P<old>.*?) 
    \s+New \s+: (?P<new>.*?)
|
    \s+(?P<value>.*?)
)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)|$)
"""
""" Field regex v3.5
# This version doesn't make clear which fields only have their current
# value, and which just have an empty 'old'.
(?sx)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)[\r\n]+
(?:
    \s+Old \s+: (?P<old>.*?) 
    \s+New \s+: (?P<new>.*?)
|
    \s+(?P<value>.*?)
)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)|$)
""" 
""" Field regex v3.7
(?sux)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)
[\r\n]+(?: \s+ Old \s+:       (?P<old>.*?)
[\r\n]+    \s+ New \s+: )?\s+ (?P<new>.*?)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)[\r\n]+\s+|$)
"""

ENTRY_PATTERN = re.compile(r"""(?sx)
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
    """)

FIELD_PATTERN = re.compile(r"""(?sx)
        ((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
        (?: Old \s+:    (?P<old>.*?)[\r\n]+
        \s+ New \s+: )? (?P<new>.*?) 
        (?=[\r\n]+(?1)\w+|$)
    """)


def __parse_fields_json(field_str: str) -> List[Dict[str, Any]]:
    fields = []

    for f in re.finditer(__AUDIT_ENTRY_FIELD_PATTERN, field_str):
        fields.append(
            {
                "fieldname": f.group("fieldname"),
                "delta": f.group("delta"),
                "old": f.group("old") if f.group("old") is not None else "",
                "new": f.group("new") if f.group("new") is not None else "",
                "value": f.group("value") if f.group("value") is not None else "",
            }
        )

    return fields


def __parse_audits_json(audit_str: str) -> List[Dict[str, Any]]:
    audits = []

    for e in re.finditer(__AUDIT_ENTRY_PATTERN, audit_str):
        audits.append(
            {
                "time": e.group("time"),
                "schema": e.group("schema"),
                "user": {
                    "name": e.group("user_name"),
                    "login": e.group("user_login"),
                    "groups": e.group("groups").split(),
                },
                "action": e.group("action"),
                "state": e.group("state"),
                "fields": __parse_fields_json(e.group("fields")),
            }
        )

    return audits


def __parse_audits_json_str(audit_str: str) -> str:
    return json.dumps(__parse_audits_json(audit_str), ensure_ascii=False)


def __parse_audits_csv(audit_str: str) -> Dict[str, List]:
    entries = []
    users = []
    groups = []
    user_groups = []
    fields = []

    for eid, e in enumerate(re.finditer(__AUDIT_ENTRY_PATTERN, audit_str)):

        uname = e.group("user_name")
        ulogin = e.group("user_login")
        gs = e.group("groups").split()

        if (uname, ulogin) not in users:
            users.append((uname, ulogin))

        for gname in gs:
            if gname not in groups:
                groups.append(gname)

            uid = users.index((uname, ulogin))
            gid = groups.index(gname)

            if (uid, gid) not in user_groups:
                user_groups.append((uid, gid))

        entries.append(
            (
                eid,
                users.index((uname, ulogin)),
                e.group("time"),
                e.group("schema"),
                e.group("action"),
                e.group("state"),
            )
        )

        for f in re.finditer(__AUDIT_ENTRY_FIELD_PATTERN, e.group("fields")):
            field = (
                eid,
                f.group("fieldname"),
                f.group("delta"),
                f.group("old") if f.group("old") is not None else "",
                f.group("new") if f.group("new") is not None else "",
                f.group("value") if f.group("value") is not None else "",
            )
            fields.append(field)

    parsed = {  # grouping all lists ('tables') & adding ids
        "entries": entries,
        "users": [(uid, uname, ulogin) for uid, (uname, ulogin) in enumerate(users)],
        "groups": [(gid, gname) for gid, gname in enumerate(groups)],
        "user_groups": user_groups,
        "fields": [
            (fid, eid, fname, delta, old, new, val)
            for fid, (eid, fname, delta, old, new, val) in enumerate(fields)
        ],
    }

    return parsed


def __parse_audits_csv_str(audit_str: str) -> Dict[str, str]:
    parsed = __parse_audits_csv(audit_str)

    entry_csv = "\n".join(
        ["eid|uid|time|schema|action|state"]
        + [
            f"{eid}|{uid}|{time}|
            #  {schema}|{action}|{state}"
            for eid, uid, time, schema, action, state in parsed["entries"]
        ]
    )

    user_csv = "\n".join(
        ["uid|uname|ulogin"]
        + [f"{uid}|{uname}|{ulogin}" for uid, uname, ulogin in parsed["users"]]
    )

    group_csv = "\n".join(
        ["gid|gname"] + [f"{gid}|{gname}" for gid, gname in parsed["groups"]]
    )

    user_groups_csv = "\n".join(
        ["uid|gid"] + [f"{uid}|{gid}" for uid, gid in parsed["user_groups"]]
    )

    field_csv = "\n".join(
        ["fid|eid|fname|delta|old|new|value"]
        + [
            rf"{fid}|{eid}|{fname}|{delta}|{old}|{new}|{value}"
            for fid, eid, fname, delta, old, new, value in parsed["fields"]
        ]
    )

    return {
        "entry": entry_csv,
        "user": user_csv,
        "group": group_csv,
        "user_group": user_groups_csv,
        "field": field_csv,
    }


def __write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def process_audit_file(audit_filename):
    base_filename = path.basename(audit_filename).split('.')[0]

    with open(audit_filename, "r", encoding="utf-8") as f:
        audit_str = f.read()

    parsed = __parse_audits_csv_str(audit_str)
    entry_filename = base_filename + "_entries.csv"
    user_filename = base_filename + "_users.csv"
    group_filename = base_filename + "_groups.csv"
    user_group_filename = base_filename + "_users_groups.csv"
    field_filename = base_filename + "_fields.csv"

    __write_file(entry_filename, parsed["entry"])
    __write_file(user_filename, parsed["user"])
    __write_file(group_filename, parsed["group"])
    __write_file(user_group_filename, parsed["user_group"])
    __write_file(field_filename, parsed["field"])