import re
from pathlib import Path

file_path = Path("f:/Whiteout Survival Bot/cogs/alliance.py")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The file has set_footer(text="Whiteout Survival | Magnus")}
# Wait, the check_hex said: Magnus") } (with a space or just terminal display?)
# No, Magnus" ) } (22 29 7d)
pattern = re.compile(r'set_footer\(text="Whiteout Survival \| Magnus"\)\}')
matches = pattern.findall(content)
print(f"Found {len(matches)} matches in alliance.py")
if matches:
    print(f"First match: {matches[0]}")
