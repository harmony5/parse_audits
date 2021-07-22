# parse-audits 📑

`parse-audits` lets you parse [ClearQuest](https://www.ibm.com/products/rational-clearquest) [AuditTrail](https://www.ibm.com/support/pages/ibm-rational-clearquest-audittrail-esignature-packages-user-guide) files to an easier to use format like **csv** or **json**.

## Installation 📦⬇

Clone this repo:

```bash
git clone https://github.com/harmony5/parse_audits
```

Then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package:

```bash
pip install -e parse_audits/
```

## Usage 🛠

To parse an Audit file, simply run:

```bash
parser_cli.py my_cq_audit_file
```

This will create a **json** file with the name `my_cq_audit_file_parsed.json` containing all audit modifications with the following structure:

```json
[
    {
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

## Contributing ✍

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License 📜⚖

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.
