"""
=============================================================================
  frontend-dashboard / scripts / maintenance.py
  Unified Maintenance Script
  ─────────────────────────────────────────────
  Replaces: fix_cyberpunk.py, replace_script.py, apply_fixes.py,
            apply_fixes2.py, apply_fixes3.py, inject_overrides.py,
            make_prof.py, upgrade_css.py

  Usage:
    python scripts/maintenance.py             # run ALL sections
    python scripts/maintenance.py --rename    # only theme rename pass
    python scripts/maintenance.py --icons     # only icon SVG fix
    python scripts/maintenance.py --html      # only HTML inline style cleanup
    python scripts/maintenance.py --css       # only site.css color upgrade
    python scripts/maintenance.py --overrides # only CSS override injection
=============================================================================
"""

import os
import re
import glob
import sys
import argparse

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE  = os.path.join(BASE_DIR, "assets", "site.css")
HTML_GLOB = os.path.join(BASE_DIR, "**", "*.html")
JS_GLOB   = os.path.join(BASE_DIR, "**", "*.js")
CSS_GLOB  = os.path.join(BASE_DIR, "**", "*.css")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Theme Rename  (viper → cyberpunk-cool)
# Replaces old theme name across all HTML, JS and CSS files.
# ═════════════════════════════════════════════════════════════════════════════
def section_rename_theme():
    print("\n[1/5] Theme rename pass (viper → cyberpunk-cool) …")
    files = []
    for pattern in [HTML_GLOB, JS_GLOB, CSS_GLOB]:
        files.extend(glob.glob(pattern, recursive=True))
    # Don't touch archive folder
    files = [f for f in files if "scripts" + os.sep + "archive" not in f]

    changed = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new = (content
                   .replace("viper",        "cyberpunk-cool")
                   .replace("Viper",        "Cyberpunk Cool")
                   .replace("VIPER",        "CYBERPUNK COOL"))
            if new != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new)
                print(f"  renamed: {os.path.relpath(file_path, BASE_DIR)}")
                changed += 1
        except Exception as e:
            print(f"  ERROR {file_path}: {e}")
    print(f"  → {changed} file(s) updated.")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — savedTheme Script Patch  (HTML <head> inline guard)
# Ensures the localStorage savedTheme guard correctly migrates viper → cyberpunk-cool
# ═════════════════════════════════════════════════════════════════════════════
OLD_SAVED_THEME = "const savedTheme = localStorage.getItem('theme') || 'cyberpunk-cool';"
NEW_SAVED_THEME = """\
let savedTheme = localStorage.getItem('theme') || 'cyberpunk-cool';
    if (savedTheme === 'viper') {
      savedTheme = 'cyberpunk-cool';
      localStorage.setItem('theme', 'cyberpunk-cool');
    }"""

OLD_INIT_THEME = "const initTheme = localStorage.getItem('theme') || 'dark';"
NEW_INIT_THEME = """\
let initTheme = localStorage.getItem('theme') || 'dark';
    if (initTheme === 'viper') {
      initTheme = 'cyberpunk-cool';
      localStorage.setItem('theme', 'cyberpunk-cool');
    }"""

def section_patch_theme_guard():
    print("\n[2/5] Patching theme guard scripts in HTML/JS …")
    files = glob.glob(HTML_GLOB, recursive=True) + glob.glob(JS_GLOB, recursive=True)
    files = [f for f in files if "scripts" + os.sep + "archive" not in f]

    changed = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new = content
            new = new.replace(OLD_SAVED_THEME, NEW_SAVED_THEME)
            new = new.replace(
                "const currentTheme = localStorage.getItem('theme') || 'cyberpunk-cool';",
                "let currentTheme = localStorage.getItem('theme') || 'cyberpunk-cool'; "
                "if (currentTheme === 'viper') { currentTheme = 'cyberpunk-cool'; localStorage.setItem('theme', 'cyberpunk-cool'); }"
            )
            new = new.replace(OLD_INIT_THEME, NEW_INIT_THEME)
            if new != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new)
                print(f"  patched: {os.path.relpath(file_path, BASE_DIR)}")
                changed += 1
        except Exception as e:
            print(f"  ERROR {file_path}: {e}")
    print(f"  → {changed} file(s) updated.")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Icon SVG Update  (cyberpunk-cool-icon)
# Updates the inline SVG icon used for the cyberpunk theme toggle button.
# ═════════════════════════════════════════════════════════════════════════════
NEW_ICON = (
    '<svg class="cyberpunk-cool-icon" viewBox="0 0 24 24" aria-hidden="true" '
    'fill="none" stroke="currentColor">'
    '<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

def section_update_icons():
    print("\n[3/5] Updating cyberpunk-cool SVG icons in HTML …")
    files = glob.glob(HTML_GLOB, recursive=True)
    files = [f for f in files if "scripts" + os.sep + "archive" not in f]

    pattern = re.compile(r'<svg\s+class="cyberpunk-cool-icon"[^>]*>.*?</svg>', re.DOTALL)
    changed = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new = pattern.sub(NEW_ICON, content)
            if new != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new)
                print(f"  icon updated: {os.path.relpath(file_path, BASE_DIR)}")
                changed += 1
        except Exception as e:
            print(f"  ERROR {file_path}: {e}")
    print(f"  → {changed} file(s) updated.")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — HTML Inline Theme-Vars Cleanup
# Strips the old verbose cyberpunk-cool CSS variable block from HTML <style>
# tags and replaces it with the lean, canonical version.
# ═════════════════════════════════════════════════════════════════════════════
CANONICAL_CYBERPUNK_VARS = """\
[data-theme="cyberpunk-cool"] {
      --radius: 8px;
      --bg-dark: #030712;
      --card-bg: rgba(17, 24, 39, 0.7);
      --glass-border: rgba(255, 255, 255, 0.05);
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --primary: #6366f1;
      --gradient-brand: linear-gradient(135deg, #fff 0%, #9ca3af 100%);
    }

    """

def section_cleanup_html_vars():
    print("\n[4/5] Cleaning up inline cyberpunk CSS vars in HTML files …")
    files = glob.glob(HTML_GLOB, recursive=True)
    files = [f for f in files if "scripts" + os.sep + "archive" not in f]

    changed = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if '[data-theme="cyberpunk-cool"] {' not in content:
                continue

            start_idx = content.find('[data-theme="cyberpunk-cool"] {')
            # Find the end — next theme block or cartoon keyframes
            end_candidates = [
                content.find('@keyframes cartoonBgShift', start_idx),
                content.find('[data-theme="cartoon"] {', start_idx),
                content.find('</style>', start_idx),
            ]
            end_idx = min(e for e in end_candidates if e != -1)

            if start_idx != -1 and end_idx > start_idx:
                new = content[:start_idx] + CANONICAL_CYBERPUNK_VARS + content[end_idx:]
                if new != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new)
                    print(f"  cleaned: {os.path.relpath(file_path, BASE_DIR)}")
                    changed += 1
        except Exception as e:
            print(f"  ERROR {file_path}: {e}")
    print(f"  → {changed} file(s) updated.")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — site.css Color Upgrade
# Inside the CYBERPUNK COOL THEME section of site.css, replaces old gold
# (#FFD700) with Neon Cyan (#00FFFF) / Hot Pink (#FF00FF), improves
# glassmorphism, and ensures cyberpunk overrides are appended at end.
# ═════════════════════════════════════════════════════════════════════════════
CYBERPUNK_CSS_OVERRIDES = """
/* ── MAINTENANCE: CYBERPUNK COOL FINAL OVERRIDES ── */

/* 1. Buttons — angled, neon gradient */
[data-theme="cyberpunk-cool"] .btn,
[data-theme="cyberpunk-cool"] .cta-btn,
[data-theme="cyberpunk-cool"] .ghost-link,
[data-theme="cyberpunk-cool"] a.ghost-link.dashboard-cta,
[data-theme="cyberpunk-cool"] button:not(.floating-chat-fab):not(.theme-toggle):not(.dow-btn) {
  background: linear-gradient(45deg, #00FFFF, #00BFFF) !important;
  color: #000 !important;
  border: none !important;
  border-radius: 0 !important;
  clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px) !important;
  text-transform: uppercase !important;
  font-weight: 800 !important;
  letter-spacing: 1px !important;
  font-family: 'Outfit', sans-serif !important;
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.6) !important;
  transition: all 0.2s ease !important;
}

[data-theme="cyberpunk-cool"] .btn:hover,
[data-theme="cyberpunk-cool"] .cta-btn:hover,
[data-theme="cyberpunk-cool"] .ghost-link:hover,
[data-theme="cyberpunk-cool"] a.ghost-link.dashboard-cta:hover,
[data-theme="cyberpunk-cool"] button:not(.floating-chat-fab):not(.theme-toggle):not(.dow-btn):hover {
  background: linear-gradient(45deg, #FF00FF, #FF1493) !important;
  box-shadow: 0 0 25px rgba(255, 0, 255, 0.9) !important;
  color: #fff !important;
  transform: scale(1.05) !important;
}

/* 2. Chat FAB — perfect circle */
[data-theme="cyberpunk-cool"] .floating-chat-fab {
  border-radius: 50% !important;
  clip-path: circle(50% at 50% 50%) !important;
  width: 60px !important;
  height: 60px !important;
  padding: 0 !important;
  background: linear-gradient(135deg, #00FFFF, #8A2BE2) !important;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.6) !important;
  border: 2px solid #FF00FF !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
[data-theme="cyberpunk-cool"] .floating-chat-fab:hover {
  background: linear-gradient(135deg, #FF00FF, #00BFFF) !important;
  box-shadow: 0 0 25px rgba(255, 0, 255, 0.8) !important;
  border-color: #00FFFF !important;
  transform: scale(1.1) !important;
}

/* 3. Hero grid — front page only */
[data-theme="cyberpunk-cool"] .hero .grid-bg {
  opacity: 0.25 !important;
  display: block !important;
  background-image:
    linear-gradient(rgba(0, 255, 255, 0.25) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 0, 255, 0.25) 1px, transparent 1px) !important;
}

/* 4. Live Command Center */
[data-theme="cyberpunk-cool"] .hero-live-feed { display: none !important; }
[data-theme="cyberpunk-cool"] .live-command-center { display: flex !important; }
"""

def section_upgrade_css():
    print("\n[5/5] Upgrading site.css (color pass + override injection) …")
    if not os.path.exists(CSS_FILE):
        print(f"  ERROR: CSS file not found at {CSS_FILE}")
        return

    with open(CSS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Color replacement inside cyberpunk section only
    start_marker = "CYBERPUNK COOL THEME"
    end_marker   = "/* Footer"
    start_idx = content.find(start_marker)
    end_idx   = content.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        pre   = content[:start_idx]
        mid   = content[start_idx:end_idx]
        post  = content[end_idx:]

        replacements = {
            'rgba(255, 215, 0, 0.5)':  'rgba(0, 255, 255, 0.5)',
            'rgba(255, 215, 0, 0.2)':  'rgba(255, 0, 255, 0.2)',
            'rgba(255, 215, 0, 0.8)':  'rgba(0, 255, 255, 0.8)',
            'rgba(255, 215, 0, 0.35)': 'rgba(255, 0, 255, 0.35)',
            'rgba(255, 215, 0, 0.6)':  'rgba(0, 255, 255, 0.6)',
            'rgba(255, 215, 0, 0.1)':  'rgba(0, 255, 255, 0.1)',
            'rgba(255, 215, 0, 0.15)': 'rgba(255, 0, 255, 0.15)',
            'rgba(255, 215, 0, 0.3)':  'rgba(0, 255, 255, 0.3)',
            'rgba(255, 215, 0, 0.4)':  'rgba(255, 0, 255, 0.4)',
            'box-shadow: 0 0 4px #FFD700':  'box-shadow: 0 0 4px #00FFFF',
            'box-shadow: 0 0 8px #FFD700':  'box-shadow: 0 0 8px #00FFFF',
            'border: 1px solid #FFD700':    'border: 1px solid #00FFFF',
            'border: 2px solid #FFD700':    'border: 2px solid #FF00FF',
            '#FFD700': '#00FFFF',
            'backdrop-filter: blur(12px);': 'backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);',
        }
        for old, new in replacements.items():
            mid = mid.replace(old, new)

        content = pre + mid + post
        print("  Color pass applied to CYBERPUNK COOL section.")
    else:
        print("  WARNING: Could not find CYBERPUNK COOL section markers. Skipping color pass.")

    # Append overrides only if not already present
    sentinel = "MAINTENANCE: CYBERPUNK COOL FINAL OVERRIDES"
    if sentinel not in content:
        content += CYBERPUNK_CSS_OVERRIDES
        print("  CSS overrides appended.")
    else:
        print("  CSS overrides already present. Skipping.")

    with open(CSS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("  → site.css saved.")


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Unified maintenance script for the frontend-dashboard."
    )
    parser.add_argument("--rename",    action="store_true", help="Run theme rename pass only")
    parser.add_argument("--guard",     action="store_true", help="Run theme guard patch only")
    parser.add_argument("--icons",     action="store_true", help="Run icon SVG update only")
    parser.add_argument("--html",      action="store_true", help="Run HTML inline vars cleanup only")
    parser.add_argument("--css",       action="store_true", help="Run site.css upgrade only")
    args = parser.parse_args()

    run_all = not any(vars(args).values())

    if run_all or args.rename:
        section_rename_theme()
    if run_all or args.guard:
        section_patch_theme_guard()
    if run_all or args.icons:
        section_update_icons()
    if run_all or args.html:
        section_cleanup_html_vars()
    if run_all or args.css:
        section_upgrade_css()

    print("\n✅  Maintenance complete.\n")

if __name__ == "__main__":
    main()
