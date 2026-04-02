with open("f:/Whiteout Survival Bot/cogs/alliance.py", "rb") as f:
    content = f.read()
    # Find the corrupted line
    marker = b'set_footer(text="Whiteout Survival'
    idx = content.find(marker)
    if idx != -1:
        # Print the next 100 bytes
        print(content[idx:idx+100])
