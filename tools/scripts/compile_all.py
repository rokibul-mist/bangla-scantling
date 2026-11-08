# -*- coding: utf-8 -*-
import os
import sys

from build_tables_md import get_markdown_content
from tables_part1 import build_part1
from tables_part2 import build_part2
from tables_part3 import build_part3
from tables_part4 import build_part4
from tables_part5 import build_part5
from tables_part6 import build_part6
from tables_part7 import build_part7

def main():
    parts = [
        get_markdown_content(),
        build_part1(),
        build_part2(),
        build_part3(),
        build_part4(),
        build_part5(),
        build_part6(),
        build_part7(),
    ]
    
    full_md = "\n\n".join(parts) + "\n"
    
    out_files = [
        "Tables.md",
        os.path.join("rules_markdown", "01_scantling_tables_schedule.md")
    ]
    
    for path in out_files:
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_md)
        print(f"Written: {path} ({len(full_md)} characters, {len(full_md.splitlines())} lines)")

if __name__ == '__main__':
    main()
