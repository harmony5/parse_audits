#!/usr/bin/env python3

import typer
from parse_audits.parse_audits import process_audit_file


def main(audit_filename: str):
    typer.echo(f"Proccessing CQ Audit file: {audit_filename}")
    process_audit_file(audit_filename)
    typer.echo("Finished proccessing")


if __name__ == "__main__":
    typer.run(main)