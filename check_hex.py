with open("f:/Whiteout Survival Bot/cogs/alliance.py", "rb") as f:
    content = f.read()
    # Find 'Whiteout Survival' then the characters after it
    marker = b'Whiteout Survival'
    idx = content.find(marker)
    if idx != -1:
        # Print the next 20 bytes in hex
        print(content[idx:idx+30].hex())
        print(content[idx:idx+30])
