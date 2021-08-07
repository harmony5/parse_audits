# AuditTrail Regexes

A compilation of the regexes used by the library and their evolution.

## General regexes (deprecated)

### General regex v1

```regexp
((?<=====START====\n)(?P<content>.*?)(?=====END====))+
```

### General regex v2

```regexp
((?<=====START====\n)
    (?P<entry>

    Time\s+:\s+
    (?P<time>
        (?P<year>\d{4})-
        (?P<month>\d{2})-
        (?P<day>\d{2})\s+
        (?P<hour>\d{2}):
        (?P<minute>\d{2}):
        (?P<second>\d{2})\s+
        (?P<timezone>[+-]?\d{2}:\d{2}))(?:\n|\r\n?)

    Schema\s+Rev\s+:\s+
    (?P<schema>\d+)(?:\n|\r\n?)

    User\s+Name\s+:\s+
    (?P<user_name>[A-Za-z ]+)(?:\n|\r\n?)

    User\s+Login\s+:\s+
    (?P<user_login>[uU]\d+)(?:\n|\r\n?)

    User\s+Groups\s+:\s+
    (?P<user_groups>[\w\b ]+)(?:\n|\r\n?)

    Action\s+:\s+
    (?P<action>[\w\b ]+)(?:\n|\r\n?)

    State\s+:\s+
    (?P<state>[\w\b ]+)(?:\n|\r\n?)

    ==Fields==(?:\n|\r\n?)
    (?P<fields>
        ((?P<fieldname>\w+(?=\s+\(\d+:\d+\)))(?:\n|\r\n?)
            \s+Old\s+:\s+
            (?P<old_value>.+?(?=\s+New))(?:\n|\r\n?)
            \s+New\s+:\s+
            (?P<new_value>.+?(?=\w+\s+\(\d+:\d+\)
                                |====END====))
        )+)(?:\n|\r\n?))
    (?=====END====))+
```

### General regex v3

```regexp
(?<=====START====\n)                # Start of audit entry
        (?P<entry>

        (?<=Time\s{11}:\s{4})       # Time of the modification
        (?P<time>
                \d{4}-              # Year
                \d{2}-              # Month
                \d{2}\s             # Day
                \d{2}:              # Hour
                \d{2}:              # Minute
                \d{2}\s             # Second
                [+-]?\d{2}:\d{2}    # Timezone
        )(?=\n)

        (?<=Schema\sRev\s{5}:\s{4}) # Schema revision
        (?P<schema>\d+)(?:\n|\r\n?)

        (?:User\s+Name\s+:\s+)      # User that modified the record
        (?P<user_name>[A-Za-z ]+)(?:\n|\r\n?)

        (?:User\s+Login\s+:\s+)     # Login used
        (?P<user_login>[uU]\d+)(?:\n|\r\n?)

        (?:User\s+Groups\s+:\s+)    # Groups, duh!
        (?P<user_groups>[\w\b ]+)(?:\n|\r\n?)

        (?:Action\s+:\s+)           # Action executed on the record
        (?P<action>[\w\b ]+)(?:\n|\r\n?)

        (?:State\s+:\s+)            # State of the record
        (?P<state>[\w\b ]+)(?:\n|\r\n?)

        (?:==Fields==(\n|\r\n?))
        (?P<fields>
            # Fieldname followed by (old_length:new_length)
            (?P<fieldname>\w+(?:\s+\(\d+:\d+\)))

            (?:(\n|\r\n?)\s+Old\s+:\s+)
            (?P<old>.+?(?:(\n|\r\n?)\s+New\s+:))

            (?:(\n|\r\n?)\s+New\s+:\s+)

            # All characters followed by another field or the end of the entry (====END====)
            (?P<new>.+?(?:((\n|\r\n?)\w+\s+\(\d+:\d+\)(\n|\r\n?))|((\n|\r\n?)====END====)))
        )+

        )(?:====END====)  # End of audit entry
```

### General regex v3.5

```regexp
(?<=====START====\n)
    (?P<entry>
        (?<=Time           :    )
        (?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2})(?=\n)

        (?<=Schema Rev     :    )
        (?P<schema>\d+?)(?=\n)

        (?<=User Name      :    )
        (?P<user_name>[A-Za-z ]+?)(?=\n)

        (?<=User Login     :    )
        (?P<user_login>[uU]\d+?)(?=\n)

        (?<=User Groups    :    )
        (?P<user_groups>[\w\b ]+?)(?=\n)

        (?<=Action         :    )
        (?P<action>[\w\b ]+?)(?=\n)

        (?<=State          :    )
        (?P<state>[\w\b ]+?)(?=\n)

        (?<===Fields==\n)
        (?P<field>
            (?P<fieldname>\w+?)(?:\s+)(?P<delta>\(\d+:\d+\))(?=\n)
            (?<=    Old :    )
            (?P<old>.+?)(?=\n    New :    )
            (?<=    New :    )
            (?P<new>.+?)(?=(\n\w+\s+\(\d+:\d+\)\n)|\n====END====)
        )+
    )(?=====END====)
```

## Entry regexes

Matches the _"metadata"_ of an AuditTrail entry, consisting of the headers before the **Fields** section.

### Entry regex v1.0

```regexp
(?s)
(?<=====START====\n)
(?P<entry>
(?:Time           :    )(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2})(?:\n)
(?:Schema Rev     :    )(?P<schema>\d+?)(?:\n)
(?:User Name      :    )(?P<user_name>[A-Za-z ]+?)(?:\n)
(?:User Login     :    )(?P<user_login>[uU]\d+?)(?:\n)
(?:User Groups    :    )(?P<user_groups>[\w\b ]+?)(?:\n)
(?:Action         :    )(?P<action>[\w\b ]+?)(?:\n)
(?:State          :    )(?P<state>[\w\b ]*?)(?:\n)
(?:==Fields==\n)
(?P<fields>.+?)
)(?=\n====END====)
```

### Entry regex v1.2

Minor changes to `(?P<user_name>)` and `(?P<user_login>)` groups.

```regexp
(?<=====START====\n)
(?P<entry>
(?:Time           :    )(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2})(?:\n)
(?:Schema Rev     :    )(?P<schema>\d+?)(?:\n)
(?:User Name      :    )(?P<user_name>[\w ]+?)(?:\n)
(?:User Login     :    )(?P<user_login>(?:[uU]\d+?|\w+?))(?:\n)
(?:User Groups    :    )(?P<groups>[\w ]+?)(?:\n)
(?:Action         :    )(?P<action>[\w ]+?)(?:\n)
(?:State          :    )(?P<state>[\w ]*?)(?:\n)
(?:==Fields==\n)
(?P<fields>.+?)
)(?=\n====END====)
```

### Entry regex v2.0

```regexp
(?s)(?x)
====START====\v
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
```

### Entry regex v2.5

```regexp
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
```

## Field regexes

### Field regex v1.0

```regexp
(?s)
(?P<fieldname>\w+?)(?:\s+)(?P<delta>\(\d+(:\d+)?\))(?:\n)
(?:
(?:    Old :    )(?P<old>.+?)(?=\n    New :    )
(?:\n    New :    )(?P<new>.+?)(?=\n\w+\s+\(\d+:\d+\)\n    Old :    |\n====END====|$)
|(?:        )(?P<value>.+?)(?=\n\w+\s+\(\d+\)\n        |\n====END====|$)
)
```

### Field regex v1.2

Change quantifier **+** to **\*** in `(?P<old>)`, `(?P<new>)` and `(?P<value>)`

```regexp
(?s)
(?P<fieldname>\w+?)(?:\s+)(?P<delta>\(\d+(:\d+)?\))(?:\n)
(?:
(?:    Old :    )(?P<old>.*?)(?=\n    New :    )
(?:\n    New :    )(?P<new>.*?)(?=\n\w+\s+\(\d+:\d+\)\n    Old :    |\n====END====|$)
|(?:        )(?P<value>.*?)(?=\n\w+\s+\(\d+\)\n        |\n====END====|$)
)
```

### Field regex v2.0

This version makes clear which fields have an `old` and a `new` value, and which ones just have their current value

```regexp
(?sx)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)[\r\n]+
(?:
    \s+Old \s+: (?P<old>.*?)
    \s+New \s+: (?P<new>.*?)
|
    \s+(?P<value>.*?)
)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)|$)
```

### Field regex v2.5

This version doesn't make clear which fields only have their current value, and which just have an empty `old`.

```regexp
(?sx)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)[\r\n]+
(?:
    \s+Old \s+:    (?P<old>.*?)
    \s+New \s+: )? (?P<new>.*?)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)|$)
```

### Field regex v2.7

```regexp
(?sux)
(?P<field_name>\S+)\s+ \((?P<delta>\d+(?::\d+)?)\)
[\r\n]+(?:  \s+ Old \s+:        (?P<old>.*?)
[\r\n]+     \s+ New \s+: )?\s+  (?P<new>.*?)
(?=[\r\n]+\w+\s+ \(\d+(?::\d+)?\)[\r\n]+\s+|$)
```

### Field regex v3.0

```regexp
(?sx)
((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
(?: Old \s+:    (?P<old>.*?)[\r\n]+
\s+ New \s+: )? (?P<new>.*?)
(?=[\r\n]+(?1)\w+|$)
```

### Field regex v3.1

This version strips the trailing whitespace from the `old` and `new` values

```regexp
(?sx)
((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
(?: Old \s+: [\t\f ]+ (?P<old>.*?) [\r\n]+
\s+ New \s+: \s+)?    (?P<new>.+?)
(?=[\r\n]+(?1)\w|$)
```

### Field regex v3.3

Adds the [\t\f ] whitespace before the `new` value to make it more consistent with the `old` value. Also removes \w in the lookahead, to allow for empty fields?

```regexp
(?sx)
((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
(?: Old \s+: [\t\f ]+   (?P<old>.*?) [\r\n]+
\s+ New \s+: [\t\f ]+)? (?P<new>.*?)
(?=[\r\n]+(?1)|$)
```

### Field regex v3.5

Add a new branch in the lookahead, allowing the regex to parse all fields in the file without first having to parse each entry

```regexp
(?sx)
((?P<field_name>\S+)\s+\((?P<delta>\d+(?::\d+)?)\)[\r\n]+\s+)
(?: Old \s+: [\t\f ]+   (?P<old>.*?) [\r\n]+
\s+ New \s+: [\t\f ]+)? (?P<new>.*?)
(?=[\r\n]+(?1)|[\r\n]+====END====|$)
```
