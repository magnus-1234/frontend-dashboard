import os
import re
from pathlib import Path

def repair_footers():
    cogs_dir = Path("f:/Whiteout Survival Bot/cogs")
    
    # 1. Broad cleanup for trailing garbage on the same line
    # Matches set_footer(...) followed by any non-whitespace garbage until newline
    trailing_garbage_pattern = re.compile(r'set_footer\(text="Whiteout Survival\s*\|\s*Magnus"\)[ \t]*[^\s\n#][^\n]*')
    
    # 2. Specific fix for multi-line corruption in fid_commands.py
    # Matches set_footer followed by incorrectly indented icon_url on next lines
    multiline_pattern = re.compile(
        r'embed\.set_footer\(text="Whiteout Survival \| Magnus"\)\s+'
        r'icon_url="(.*?)"\s+'
        r'\)',
        re.MULTILINE
    )

    # 3. Specific fix for the - 10} pattern in gift_operations.py
    gift_ops_pattern = re.compile(r'embed\.set_footer\(text="Whiteout Survival \| Magnus"\)\s*-\s*\d+\}[^\n]*')

    modified_files = []
    
    for file_path in cogs_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orig_content = content
            
            # Apply broad cleanup
            content = trailing_garbage_pattern.sub(r'set_footer(text="Whiteout Survival | Magnus")', content)
            
            # Apply multiline fix
            content = multiline_pattern.sub(r'embed.set_footer(text="Whiteout Survival | Magnus", icon_url="\1")', content)
            
            # Apply specific gift_ops fix
            content = gift_ops_pattern.sub(r'embed.set_footer(text="Whiteout Survival | Magnus")', content)
            
            # Extra safety: check for any remaining )} or ") 
            content = re.sub(r'set_footer\(text="Whiteout Survival \| Magnus"\)\}\s*[^\n]*', r'set_footer(text="Whiteout Survival | Magnus")', content)
            content = re.sub(r'set_footer\(text="Whiteout Survival \| Magnus"\)"\)\s*[^\n]*', r'set_footer(text="Whiteout Survival | Magnus")', content)

            if content != orig_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files.append(file_path.name)
                print(f"🔧 Deep Repaired corrupted footers in {file_path.name}")
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            
    return modified_files

if __name__ == "__main__":
    repaired = repair_footers()
    print(f"\n--- Total Files Deep Repaired: {len(repaired)} ---")
