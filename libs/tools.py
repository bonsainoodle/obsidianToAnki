import re


def replace_latex_delimiters(input_text):
    pattern = r"\$\$(.*?)\$\$|\$(.*?)\$"

    output_text = re.sub(
        pattern,
        lambda match: f"[latex]${match.group(1) or match.group(2)}$[/latex]",
        input_text,
    )

    return output_text


def remove_text(input_text):
    pattern = r"\[\[.*?\]\]|\#.*?(\s|$)"

    output_text = re.sub(pattern, "", input_text)

    return output_text
