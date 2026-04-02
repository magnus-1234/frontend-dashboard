import re
from pathlib import Path

file_path = Path("f:/Whiteout Survival Bot/cogs/alliance.py")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'Whiteout Survival')
matches = pattern.findall(content)
print(f"Found {len(matches)} matches for 'Whiteout Survival' in alliance.py")
if matches:
    print(f"First match starts at: {content.find('Whiteout Survival')}")
    snippet = content[content.find('Whiteout Survival')-20:content.find('Whiteout Survival')+100]
    print(f"Snippet: {repr(snippet)}")
