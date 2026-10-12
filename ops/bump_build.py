"""Write a fresh BUILD_SERIAL into src/graderprobe/_provenance.py.

Run before every release build so each published distribution carries a unique
serial. Usage: python ops/bump_build.py
"""

import re
import sys
import uuid
from pathlib import Path

TARGET = (
    Path(__file__).resolve().parent.parent / "src" / "graderprobe" / "_provenance.py"
)

def main() -> None:
    source = TARGET.read_text(encoding="utf-8")
    serial = str(uuid.uuid4())
    new_line = f'BUILD_SERIAL = "{serial}"'
    updated, count = re.subn(r'BUILD_SERIAL = "[^"]*"', new_line, source)
    if count != 1:
        sys.exit("error: BUILD_SERIAL line not found in _provenance.py")
    TARGET.write_text(updated, encoding="utf-8")
    print(new_line)


if __name__ == "__main__":
    main()
