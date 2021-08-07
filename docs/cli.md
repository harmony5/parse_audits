# `parse-audits`

A tool to parse ClearQuest AuditTrail files to an easier-to-use format.

**Usage**:

```console
$ parse-audits [OPTIONS] AUDIT_FILENAME
```

**Arguments**:

-   `AUDIT_FILENAME`: The path to the audit file to parse. [required]

**Options**:

-   `-f, --format [csv|xlsx|json]`: Parse the AuditTrail file to the specified format. [default: json]
-   `-o, --output TEXT`: Save the parsed file with the specified filename.
-   `--install-completion`: Install completion for the current shell.
-   `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
-   `--help`: Show this message and exit.
