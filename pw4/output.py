import contextlib
import curses
import io

MIN_BOX_HEIGHT = 7
MIN_BOX_WIDTH = 24
MIN_VIEW_HEIGHT = 5
MIN_VIEW_WIDTH = 20

def _safe_addstr(win, y, x, text, attr=curses.A_NORMAL):
    try:
        height, width = win.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width - 1:
            return
        win.addstr(y, x, text[:width - x - 1], attr)
    except curses.error:
        pass

def _init_curses_ui():
    with contextlib.suppress(curses.error):
        curses.curs_set(0)
    title_attr = curses.A_REVERSE | curses.A_BOLD
    selected_attr = curses.A_REVERSE | curses.A_BOLD
    normal_attr = curses.A_NORMAL
    try:
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
                background = -1
            except (curses.error, AttributeError):
                background = curses.COLOR_BLACK
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)    # title bar
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)   # selected row
            try:
                curses.init_pair(3, curses.COLOR_CYAN, background)       # normal row
            except (curses.error, ValueError):
                curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
            title_attr = curses.color_pair(1) | curses.A_BOLD
            selected_attr = curses.color_pair(2) | curses.A_BOLD
            normal_attr = curses.color_pair(3)
    except (curses.error, ValueError):
        pass  
    return title_attr, selected_attr, normal_attr


def _handle_resize(stdscr):
    try:
        height, width = stdscr.getmaxyx()
        if curses.is_term_resized(height, width):
            curses.resize_term(0, 0)
        stdscr.clear()
    except (curses.error, AttributeError):
        pass

def _draw_too_small(stdscr, message="Window too small - enlarge it."):
    stdscr.erase()
    _safe_addstr(stdscr, 0, 0, message)
    stdscr.refresh()

def curses_menu(stdscr, title, options):
    title_attr, selected_attr, normal_attr = _init_curses_ui()
    idx = 0     
    top = 0      
    while True:
        try:
            height, width = stdscr.getmaxyx()
            box_width = min(width - 2,
                            max(len(title), max(len(o) for o in options)) + 8)
            box_height = min(height - 2, len(options) + 4)
            if box_height < MIN_BOX_HEIGHT or box_width < MIN_BOX_WIDTH:
                _draw_too_small(stdscr, "Window too small. Enlarge it or press q.")
            else:
                visible = box_height - 4
                if idx < top:
                    top = idx
                elif idx >= top + visible:
                    top = idx - visible + 1
                top = max(0, min(top, len(options) - visible))
                start_y = max(0, (height - box_height) // 2)
                start_x = max(0, (width - box_width) // 2)
                stdscr.erase()
                win = stdscr.derwin(box_height, box_width, start_y, start_x)
                win.erase()
                win.border()
                _safe_addstr(win, 0, 2, f" {title} ", title_attr)
                for row, option in enumerate(options[top:top + visible]):
                    style = selected_attr if top + row == idx else normal_attr
                    _safe_addstr(win, 2 + row, 2,
                                 option.ljust(box_width - 4), style)
                if top > 0:
                    _safe_addstr(win, 1, box_width - 4, "^", normal_attr)
                if top + visible < len(options):
                    _safe_addstr(win, box_height - 2, box_width - 4, "v", normal_attr)
                _safe_addstr(win, box_height - 1, 2,
                             "Up/Down move  Enter select  q quit", curses.A_DIM)
                stdscr.refresh()
                win.refresh()
        except curses.error:
            pass   
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            _handle_resize(stdscr)
        elif key in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            return idx
        elif key in (ord('q'), 27):  # 27 = Esc
            return None

def curses_show(stdscr, title, text):
    """Scrollable read-only viewer for a block of text."""
    title_attr, _, _ = _init_curses_ui()
    lines = text.splitlines() or ["(nothing to show)"]
    top = 0
    while True:
        height, width = stdscr.getmaxyx()
        visible = max(1, height - 3)
        try:
            if height < MIN_VIEW_HEIGHT or width < MIN_VIEW_WIDTH:
                _draw_too_small(stdscr, "Window too small. Enlarge it.")
            else:
                top = max(0, min(top, len(lines) - visible))
                stdscr.erase()
                _safe_addstr(stdscr, 0, 0, f" {title} ".center(width, "="),
                             curses.A_BOLD | title_attr)
                for i, line in enumerate(lines[top:top + visible]):
                    _safe_addstr(stdscr, 2 + i, 2, line[:max(0, width - 4)])
                _safe_addstr(stdscr, height - 1, 0,
                             .center(width, "-"),
                             curses.A_DIM)
                stdscr.refresh()
        except curses.error:
            pass   
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            _handle_resize(stdscr)
        elif key == curses.KEY_DOWN:
            top = min(max(0, len(lines) - visible), top + 1)
        elif key == curses.KEY_UP:
            top = max(0, top - 1)
        elif key == curses.KEY_NPAGE:
            top = min(max(0, len(lines) - visible), top + visible)
        elif key == curses.KEY_PPAGE:
            top = max(0, top - visible)
        else:
            return

def show_menu(title, options):
    return curses.wrapper(curses_menu, title, options)

def show_text(title, text):
    curses.wrapper(curses_show, title, text)

def capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()
