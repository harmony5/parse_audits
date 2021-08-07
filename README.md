# parse-audits 📑

`parse-audits` lets you parse [ClearQuest](https://www.ibm.com/products/rational-clearquest) [AuditTrail](https://www.ibm.com/support/pages/ibm-rational-clearquest-audittrail-esignature-packages-user-guide) files to an easier to use format like **csv** or **json**.

## Installation 📦⬇

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package:

```console
pip install parse-audits
```

## Usage 🛠

To parse an AuditTrail file, simply run:

```console
parse-audits my_cq_audit_file
```

This will create a **json** file with the name `my_cq_audit_file_parsed.json` containing all audit modifications with the following structure:

```jsonc
[
    {
        "entry_id": 1,

        // Time of the modification with the format 'YYYY-MM-DD HH:mm:SS [+-]HHmm'
        "time": "2020-12-31 00:00:00 -0400",

        // Schema version at the time of record modification
        "schema": "01",

        // User who made the modification
        "user_name": "Jane Doe",

        // User login number
        "user_login": "U12345",

        // Groups the user was in at the time of the modification
        "user_groups": ["group_1", "group_2", "group_3"],

        // Action that modified the record
        "action": "Update",

        // State of the record after the action
        "state": "Modified",

        // Fields modified by the action
        "fields": [
            {
                "field_name": "Email",

                // Length of 'old' value / length of 'new' value
                "delta": "20:22",

                // Value before the modification
                "old": "jane.doe@example.com",

                // Value after the modification
                "new": "jane.doe99@example.com"
            },
            {
                "field_name": "Description",

                // For some fields only their current (new) value is saved.
                // In these cases, delta is only the length of this value
                "delta": "35",

                "old": "",

                // Current value of the field
                "new": "This is the new record description."
            }
        ]
    }
    // Some other entries in the AuditTrail file
]
```

You can also pass a `--format` or `-f` option to the tool to parse the file in an specific format.

For example, if we wanted to parse the file to csv:

```console
parse-audits -f csv my_cq_audit_file
```

This will create a **csv** file named `my_cq_audit_file_parsed.csv` with `|` as delimiter and with values **not enclosed** in quotes. For example:

![Parsed csv](docs/csv-example.png)

Or we could parse the file to Excel:

```console
parse-audits -f xlsx my_cq_audit_file
```

This will create an **Excel** file named `my_cq_audit_file_parsed.xlsx` with 3 spreadsheets:

-   **Audit Entries** contains the entries metadata, things like the time, schema, the user who made the change, the action taken and the state

![Audit Entries](docs/excel-example-1.png)

-   **Audit Fields** contains the fields data and the corresponding entry_id and time

![Audit Fields](docs/excel-example-2.png)

-   **User Groups** contains the user_name, user_login and the group_names of the users found in the file

![User Groups](docs/excel-example-3.png)

Currently supported formats are `csv`, `json` and `xlsx`. By default, `--format` is set to `json`.

For more help on how to use the tool, you can type:

```console
parse-audits --help
```

Or see [CLI docs](docs/cli.md).

## Contributing ✍

[Pull requests](https://github.com/harmony5/parse_audits/pulls/new) are welcome. For major changes, [bug fixes](https://github.com/harmony5/parse_audits/issues/new?template=bug_report.md&labels=bug) or [feature requests](https://github.com/harmony5/catchup/issues/new?template=feature_request.md), please open an issue first to discuss what you would like to change.

## License 📜⚖

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.
