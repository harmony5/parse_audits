# parse-audits

`parse-audits` lets you parse [ClearQuest](https://www.ibm.com/products/rational-clearquest) [AuditTrail](https://www.ibm.com/support/pages/ibm-rational-clearquest-audittrail-esignature-packages-user-guide) files to an easier to use format like **csv**.

## Installation

Clone this repo:

```bash
git clone https://github.com/harmony5/parse_audits
```

Then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package:

```bash
pip install -e parse_audits/
```

## Usage

To parse an Audit file, simply run:

```bash
main.py my_cq_audit_file
```

This will create 5 **csv** files:

- **my_cq_audit_file_entries.csv**: contains general information about entries in the audit file, like time of the entry, schema version, action taken on the record, and the state of the record.

- **my_cq_audit_file_users.csv**: information about the users, like username and the login id.

- **my_cq_audit_file_groups.csv**: a list of all groups found on the audit file.

- **my_cq_audit_file_users_groups.csv**: contains the relations between the users and the groups they're in.

- **my_cq_audit_file_fields.csv**: information about modified fields, including the field name, delta (length of the text value before and after changing the record), the old value, the new value.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.
