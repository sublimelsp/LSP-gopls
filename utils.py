import textwrap


def reformat(text: str) -> str:
    return textwrap.dedent(text).strip()