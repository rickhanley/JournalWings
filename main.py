# main now does nothing more than call run and ultimately
# catch any exceptions


from modules.pipeline import run
import traceback
import sys

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
    except KeyboardInterrupt as e:
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: ")
        traceback.print_exc()
        input("     Press Enter to close this window...")
        sys.exit(1)
