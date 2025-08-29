# main now does nothing more than call run and ultimately
# catch any exceptions


import sys
import traceback

from modules.pipeline import run

if __name__ == "__main__":
    try:
        run()
    except ValueError as e:
        print(e)
        try:
            input("     Press Enter to close this window...")
        except KeyboardInterrupt:
            pass
        sys.exit(1)
    except RuntimeError as e:
        print(f"{e}")
        input("     Press Enter to close this window...")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        print("[!] Unexpected error: ")
        traceback.print_exc()
        input("     Press Enter to close this window...")
        sys.exit(1)
