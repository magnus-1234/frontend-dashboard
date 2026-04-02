import os
import sys
import py_compile
from pathlib import Path

def verify_cogs():
    cogs_dir = Path("f:/Whiteout Survival Bot/cogs")
    print(f"--- Verifying Cogs in {cogs_dir} ---")
    
    errors = 0
    for file_path in cogs_dir.glob("*.py"):
        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✅ {file_path.name}: Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"❌ {file_path.name}: Syntax Error!")
            print(f"   {e.msg}")
            errors += 1
        except Exception as e:
            print(f"❌ {file_path.name}: Unexpected Error: {e}")
            errors += 1
            
    print(f"\n--- Total Errors: {errors} ---")
    return errors

if __name__ == "__main__":
    sys.exit(verify_cogs())
