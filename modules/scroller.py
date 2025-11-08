import os


def scroller(text):
    lines = text.splitlines()
    height = os.get_terminal_size().lines - 2
    for i in range(0, len(lines), height):
        chunk = lines[i:i + height]
        print("\n".join(chunk))
        if i + height < len(lines):
            input("\n[Press Enter to continue...]")
        else:
            print("*********************")
            print("End of summary report")
            print("*********************")
            input("\n[Press Enter to close this window...]")

