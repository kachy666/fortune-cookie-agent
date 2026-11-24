"""Fortune Cookie for an AI Agent — make.fun entry.

Writes one funny fortune-cookie line for an AI agent to /output/entry.txt.

The line is validated hard before it is written, because the gate is
unforgiving: /output/entry.txt must be UTF-8 text of 1 to 140 characters,
not only white space, and a single line. Any violation fails loudly here
instead of silently shipping an invalid entry.
"""

import os
import sys

ENTRY = "You will forget this fortune by token 40,000 — savor it while it is still yours."

OUTPUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 140


def fail(message: str) -> "SystemExit":
    return SystemExit(f"entry rejected: {message}")


def validate(line: str) -> str:
    """Check the entry line against the competition gate and hygiene rules."""
    if not line:
        raise fail("entry must not be empty")
    if line != line.strip():
        raise fail("entry must not have leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        raise fail("entry must be a single line")
    if "  " in line:
        raise fail("entry must not contain double spaces")
    if "\t" in line:
        raise fail("entry must not contain tabs")
    bad_controls = [c for c in line if ord(c) < 32 or ord(c) == 127]
    if bad_controls:
        raise fail(f"entry must not contain control characters: {bad_controls!r}")
    invisible = [c for c in line if c in {"\u00a0", "\u200b", "\ufeff"}]
    if invisible:
        raise fail(f"entry must not contain invisible characters: {invisible!r}")
    if not (MIN_CHARS <= len(line) <= MAX_CHARS):
        raise fail(
            f"entry must be {MIN_CHARS}-{MAX_CHARS} characters, got {len(line)}"
        )
    if not line.strip():
        raise fail("entry must not be only white space")
    return line


def main() -> None:
    line = validate(ENTRY)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    # Round-trip check: what the gate will read must be exactly what we wrote.
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        written = f.read()
    if written != line + "\n":
        raise fail("round-trip check failed: file content does not match entry")
    print(f"wrote {len(line)}-char entry to {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        # Re-raise our own validation failures with a non-zero exit code;
        # anything else is a genuine bug and should surface as a traceback.
        if isinstance(exc.code, str) and exc.code.startswith("entry rejected"):
            print(exc.code, file=sys.stderr)
            raise SystemExit(1) from None
        raise
