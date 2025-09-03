import difflib
import os
import sys

import click


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("file1", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("file2", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="File to save the diff to. If not specified, output will be printed to stdout.",
)
@click.option(
    "--context", "-c", type=int, help="Generates a context diff with N lines of context. Overrides --unified."
)
@click.option(
    "--unified", "-u", type=int, default=3, help="Generates a unified diff with N lines of context. Default is 3."
)
@click.option("--html", "-H", is_flag=True, help="Generates diff in HTML format. Overrides --context and --unified.")
def diff_tool(file1, file2, output, context, unified, html):
    """High-performance file DIFF tool. Displays differences between FILE1 and FILE2."""
    try:
        with open(file1, "r", encoding="utf-8") as f1:
            lines1 = f1.readlines()
        with open(file2, "r", encoding="utf-8") as f2:
            lines2 = f2.readlines()
    except Exception as e:
        click.echo(f"Error: Failed to read file '{file1}' or '{file2}' - {e}", err=True)
        sys.exit(1)

    from_file_name = os.path.basename(file1)
    to_file_name = os.path.basename(file2)
    diff_output_lines = []
    output_is_html = False

    if html:
        if context is not None:
            click.echo("Warning: --context option will be ignored because --html is specified.", err=True)
        if unified != 3:
            click.echo("Warning: --unified option will be ignored because --html is specified.", err=True)
        differ = difflib.HtmlDiff()
        diff_str = differ.make_file(
            lines1,
            lines2,
            fromdesc=from_file_name,
            todesc=to_file_name,
        )
        diff_output_lines = [diff_str]
        output_is_html = True
    elif context is not None:
        if unified != 3:
            click.echo("Warning: --unified option will be ignored because --context is specified.", err=True)
        diff_output_lines = difflib.context_diff(
            lines1, lines2, fromfile=from_file_name, tofile=to_file_name, n=context
        )
    else:
        diff_output_lines = difflib.unified_diff(
            lines1, lines2, fromfile=from_file_name, tofile=to_file_name, n=unified
        )

    if output:
        try:
            with open(output, "w", encoding="utf-8") as outfile:
                if output_is_html:
                    outfile.write(diff_output_lines[0])
                else:
                    outfile.writelines(diff_output_lines)
            click.echo(f"Diff saved to '{output}'.")
        except Exception as e:
            click.echo(f"Error: Failed to write to output file '{output}' - {e}", err=True)
            sys.exit(1)
    else:
        if output_is_html:
            click.echo(diff_output_lines[0])
        else:
            for line in diff_output_lines:
                if line.startswith("+"):
                    click.echo(click.style(line, fg="green"), nl=False)
                elif line.startswith("-"):
                    click.echo(click.style(line, fg="red"), nl=False)
                else:
                    click.echo(line, nl=False)


if __name__ == "__main__":
    diff_tool()
