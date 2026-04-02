import re
from pathlib import Path

file_path = Path("f:/Whiteout Survival Bot/cogs/alliance.py")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target: set_footer(text="Whiteout Survival | Magnus")} total servers")
# Match 1: set_footer(text="Whiteout Survival | Magnus"
# Match 2: )} total servers"
# Match 3: )
pattern = re.compile(r'(set_footer\(text="Whiteout Survival\s*\|\s*Magnus")(\)\}.*?)(\n|$)')

new_content = pattern.sub(r'\1)', content)

# Check if it worked
with open("f:/Whiteout Survival Bot/cogs/alliance_fixed.py", 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Check cogs/alliance_fixed.py")
