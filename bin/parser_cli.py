#!/usr/bin/env python3
from os import path
import typer
from parse_audits.parsers import parse_audit_text_as_json
from parse_audits.utils import _read_file, _write_file


def main(audit_filename: str):
    typer.echo(f"Proccessing CQ Audit file: {audit_filename}")
    
    parsed = parse_audit_text_as_json(_read_file(audit_filename))
    basename = path.basename(audit_filename).split(".")[0]
    _write_file(f"{basename}_parsed.json", parsed)

    typer.echo("Finished proccessing")


if __name__ == "__main__":
    typer.run(main)