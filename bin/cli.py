#!/usr/bin/env python3
from os import path
from typing import Optional

import typer

from parse_audits.parsers import Format, Parser
from parse_audits.utils import _read_file, _write_file


def main(
    audit_filename: str,
    format: Optional[Format] = typer.Option(
        Format.JSON,
        "--format",
        "-f",
        help="Parse the AuditTrail file to the specified format.",
    ),
    output_filename: Optional[str] = typer.Option(
        None,
        "--outfile",
        "-o",
        help="Save the parsed file to the specified directory/filename.",
    ),
):
    typer.echo(f"Proccessing CQ Audit file: {audit_filename}")
    audit_file = _read_file(audit_filename)

    parser = Parser(audit_file, format)
    parsed_content = parser.parse()

    if not output_filename:
        basename = path.basename(audit_filename).rsplit(".", 1)[0]
        extension = format.value
        output_filename = f"{basename}_parsed.{extension}"

    _write_file(output_filename, parsed_content, binary=(format == Format.EXCEL))
    typer.echo(f"Parsed to file {output_filename}")


if __name__ == "__main__":
    typer.run(main)
