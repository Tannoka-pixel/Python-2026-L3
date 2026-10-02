import contextlib
import io

def text_menu(title, options):
    print(f"\n--- {title} ---")
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")
    print("q. Exit")
    while True:
        try:
            choice = input("Enter your choice: ").strip()
            if choice.lower() == 'q':
                return None
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                return choice_idx
            else:
                print("Invalid choice. Please enter a number or 'q'.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")

def text_show(title, text):
    print(f"\n--- {title} ---")
    print(text)
    input("Press Enter to return to the menu...")

def capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()
