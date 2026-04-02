import os
import re
from pathlib import Path

def find_corrupted_footers():
    cogs_dir = Path("f:/Whiteout Survival Bot/cogs")
    pattern = re.compile(r'set_footer\(text="Whiteout Survival \| Magnus"\}')
    
    for file_path in cogs_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                if pattern.search(line):
                    print(f"{file_path.name}:{i+1}: {line.strip()}")
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

if __name__ == "__main__":
    find_corrupted_footers()
