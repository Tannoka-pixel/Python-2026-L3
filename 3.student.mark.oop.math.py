import contextlib
import curses
import io
import math
import random
from abc import ABC, abstractmethod

import numpy as np

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
        pass  # keep the monochrome fallback
    return title_attr, selected_attr, normal_attr
def _handle_resize(stdscr):
    """React to a KEY_RESIZE event: sync curses with the new size and force
    a full repaint on the next loop iteration."""
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
class Entity(ABC):
    def __init__(self, entity_id="", name=""):
        self._id = ""
        self._name = ""
        if entity_id:
            self.id = entity_id
        if name:
            self.name = name
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("ID must not be empty.")
        self._id = value
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Name must not be empty.")
        self._name = value
    @staticmethod
    def _ask(prompt, setter):
        while True:
            try:
                setter(input(prompt))
                return
            except ValueError as err:
                print(f"  {err}")
    def input(self):
        self._ask("  ID: ", lambda v: setattr(self, "id", v))
        self._ask("  Name: ", lambda v: setattr(self, "name", v))
    @classmethod
    @abstractmethod
    def header(cls):
        pass
    @abstractmethod
    def row(self):
        pass
    def list(self):
        print(self.row())

class Student(Entity):
    def __init__(self, student_id="", name="", dob=""):
        super().__init__(student_id, name)
        self._dob = ""
        if dob:
            self.dob = dob
    @property
    def dob(self):
        return self._dob
    @dob.setter
    def dob(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Date of birth must not be empty.")
        self._dob = value
    def input(self):
        super().input()
        self._ask("  Date of Birth (dd/mm/yyyy): ",
                  lambda v: setattr(self, "dob", v))
    @classmethod
    def header(cls):
        return f"{'ID':<12}{'Name':<30}{'DoB':<15}\n" + "-" * 57
    def row(self):
        return f"{self.id:<12}{self.name:<30}{self.dob:<15}"
class Course(Entity):
    def __init__(self, course_id="", name="", credit=""):
        super().__init__(course_id, name)
        self._credit = 0.0
        if credit != "":
            self.credit = credit
    @property
    def credit(self):
        return self._credit
    @credit.setter
    def credit(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Credit must be a number.")
        if value <= 0:
            raise ValueError("Credit must be a positive number.")
        self._credit = value

    def input(self):
        super().input()
        self._ask("  Credit: ", lambda v: setattr(self, "credit", v))
    @classmethod
    def header(cls):
        return f"{'ID':<12}{'Name':<30}{'Credit':<10}\n" + "-" * 52
    def row(self):
        return f"{self.id:<12}{self.name:<30}{self.credit:<10.1f}"
class DemoStudentFactory:
    _SURNAMES = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan",
                 "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly"]
    _MIDDLE_NAMES = ["Van", "Thi", "Khanh", "Minh", "Quoc", "Thanh", "Huu",
                     "Ngoc", "Gia", "Kim", "Anh", "Duc"]
    _GIVEN_NAMES = ["Hung", "Anh", "Linh", "Nam", "Trang", "Huy", "Long",
                    "Mai", "Yen", "Phuc", "Duc", "Trung", "Hoa", "Thu",
                    "Tuan", "Hieu", "Quyen", "Chi", "Bao", "Khoa"]
    _MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    _START_ID = 2510437
    @staticmethod
    def _ordinal(n):
        """8 -> '8th', 1 -> '1st', 22 -> '22nd' ..."""
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
    @classmethod
    def _random_name(cls):
        return (f"{random.choice(cls._SURNAMES)} "
                f"{random.choice(cls._MIDDLE_NAMES)} "
                f"{random.choice(cls._GIVEN_NAMES)}")
    @classmethod
    def _random_dob(cls, start_year=2005, end_year=2008):
        day = random.randint(1, 28)
        month = random.choice(cls._MONTHS)
        year = random.randint(start_year, end_year)
        return f"{cls._ordinal(day)} {month} {year}"
    @classmethod
    def create(cls, n=140):
        """Return a list of n students; the first one is fixed."""
        students = [Student(str(cls._START_ID), "Nguyen Khanh Hung", "8th Sep 2007")]
        for i in range(1, n):
            students.append(Student(str(cls._START_ID + i),
                                    cls._random_name(),
                                    cls._random_dob()))
        return students
class MarkBook:
    def __init__(self):
        self._marks = {}
    @staticmethod
    def _round_down(value):
        return math.floor(float(value) * 10) / 10
    def set_mark(self, course_id, student_id, mark):
        self._marks.setdefault(course_id, {})[student_id] = self._round_down(mark)
    def get_course_marks(self, course_id):
        """Return a copy so callers cannot modify the internal data."""
        return dict(self._marks.get(course_id, {}))
    def has_marks(self, course_id):
        return bool(self._marks.get(course_id))
class StudentMarkManagement:
    MENU_OPTIONS = [
        "Input Students (manual)",
        "Generate Demo Students (140, random names)",
        "Input Courses",
        "Input Marks (manual)",
        "Auto-generate Random Marks for a Course (0-20)",
        "List Courses",
        "List Students",
        "Show Marks for a Course",
        "Show GPA for a Student",
        "Sort & Show Students by GPA (Descending)",
        "Exit",
    ]
    _INPUT_DRIVEN = {
        "Input Students (manual)": "input_students",
        "Generate Demo Students (140, random names)": "generate_demo_students",
        "Input Courses": "input_courses",
        "Input Marks (manual)": "input_marks",
        "Auto-generate Random Marks for a Course (0-20)": "generate_random_marks",
        "Show Marks for a Course": "show_marks",
        "Show GPA for a Student": "show_gpa",
    }
    _DISPLAY_ONLY = {
        "List Courses": "list_courses",
        "List Students": "list_students",
        "Sort & Show Students by GPA (Descending)": "sort_students_by_gpa",
    }
    _MIN_BOX_HEIGHT = 7
    _MIN_BOX_WIDTH = 24
    _MIN_VIEW_HEIGHT = 5
    _MIN_VIEW_WIDTH = 20
    def __init__(self):
        self._students = []          # list of Student
        self._courses = []           # list of Course
        self._marks = MarkBook()
    @staticmethod
    def _read_int(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a whole number.")
    @staticmethod
    def _find(collection, entity_id):
        """Polymorphic lookup: works for both Students and Courses."""
        for item in collection:
            if item.id == entity_id:
                return item
        return None
    def _input_entities(self, factory, collection, label):
        n = self._read_int(f"Enter number of {label}s to add: ")
        for _ in range(n):
            print(f"\n{label.capitalize()} {len(collection) + 1}:")
            entity = factory()
            entity.input()
            collection.append(entity)
    def _list_entities(self, title, collection, entity_class):
        print(f"\n--- {title} ---")
        if not collection:
            print(f"No {title.split()[0].lower()} available.")
            return
        print(entity_class.header())
        for entity in collection:
            entity.list()
    def _choose_course(self, prompt):
        self.list_courses()
        course = self._find(self._courses, input(prompt).strip())
        if course is None:
            print("Course not found.")
        return course
    def _choose_student(self, prompt):
        self.list_students()
        student = self._find(self._students, input(prompt).strip())
        if student is None:
            print("Student not found.")
        return student
    def _compute_gpa(self, student_id):
        credits, marks = [], []
        for course in self._courses:
            course_marks = self._marks.get_course_marks(course.id)
            if student_id in course_marks:
                credits.append(course.credit)
                marks.append(course_marks[student_id])
        if not credits:
            return None
        credits_arr = np.array(credits, dtype=float)
        marks_arr = np.array(marks, dtype=float)
        return float(np.dot(credits_arr, marks_arr) / credits_arr.sum())
    @staticmethod
    def _gpa_table(rows):
        lines = [f"{'Rank':<6}{'ID':<12}{'Name':<30}{'GPA':<8}", "-" * 56]
        for rank, (student, gpa) in enumerate(rows, start=1):
            gpa_text = f"{gpa:.2f}" if gpa is not None else "N/A"
            lines.append(f"{rank:<6}{student.id:<12}{student.name:<30}{gpa_text:<8}")
        return "\n".join(lines)
    def input_students(self):
        self._input_entities(Student, self._students, "student")
    def generate_demo_students(self, n=140):
        self._students = DemoStudentFactory.create(n)
        print(f"Generated {n} demo students.")
    def input_courses(self):
        self._input_entities(Course, self._courses, "course")
    def input_marks(self):
        if not self._courses:
            print("No courses available. Please add courses first.")
            return
        course = self._choose_course("Enter course ID to enter marks for: ")
        if course is None:
            return
        if not self._students:
            print("No students available. Please add students first.")
            return
        print(f"\nEntering marks for course: {course.name} ({course.id})")
        print("(marks are rounded down to 1 decimal place, e.g. 8.97 -> 8.9)")
        for student in self._students:
            while True:
                raw = input(f"  Mark for {student.name} ({student.id}): ").strip()
                try:
                    mark = float(raw)
                    if not 0 <= mark <= 20:
                        raise ValueError
                    break
                except ValueError:
                    print("  Please enter a number between 0 and 20.")
            self._marks.set_mark(course.id, student.id, mark)
    def generate_random_marks(self, low=0, high=20):
        if not self._courses:
            print("No courses available. Please add courses first.")
            return
        if not self._students:
            print("No students available. Please add/generate students first.")
            return
        course = self._choose_course("Enter course ID to auto-generate marks for: ")
        if course is None:
            return
        for student in self._students:
            self._marks.set_mark(course.id, student.id, random.uniform(low, high))
        print(f"Generated random marks ({low}-{high}) for {len(self._students)} "
              f"students in {course.name} ({course.id}).")
    def list_courses(self):
        self._list_entities("Courses List", self._courses, Course)
    def list_students(self):
        self._list_entities("Students List", self._students, Student)
    def show_marks(self):
        course = self._choose_course("Enter course ID to view marks: ")
        if course is None:
            return
        if not self._marks.has_marks(course.id):
            print(f"No marks recorded yet for course {course.name} ({course.id}).")
            return
        print(f"\n--- Marks for {course.name} ({course.id}) ---")
        print(f"{'ID':<12}{'Name':<30}{'Mark':<10}")
        print("-" * 52)
        for student_id, mark in self._marks.get_course_marks(course.id).items():
            student = self._find(self._students, student_id)
            name = student.name if student else "Unknown"
            print(f"{student_id:<12}{name:<30}{mark:<10}")
    def show_gpa(self):
        student = self._choose_student("Enter student ID to compute GPA for: ")
        if student is None:
            return
        gpa = self._compute_gpa(student.id)
        if gpa is None:
            print(f"No marks recorded yet for {student.name} ({student.id}).")
            return
        print(f"\nGPA for {student.name} ({student.id}): {gpa:.2f}")
    def sort_students_by_gpa(self):
        """Sort self._students descending by GPA (numpy.argsort), then show it."""
        if not self._students:
            print("No students available.")
            return
        gpas = [self._compute_gpa(s.id) for s in self._students]
        sort_key = np.array([g if g is not None else -1.0 for g in gpas])
        order = np.argsort(-sort_key, kind="stable")
        self._students = [self._students[i] for i in order]
        gpas_sorted = [gpas[i] for i in order]
        print("\n--- Students Sorted by GPA (Descending) ---")
        print(self._gpa_table(list(zip(self._students, gpas_sorted))))
    @staticmethod
    def _curses_menu(stdscr, title, options):
        title_attr, selected_attr, normal_attr = _init_curses_ui()
        min_h = StudentMarkManagement._MIN_BOX_HEIGHT
        min_w = StudentMarkManagement._MIN_BOX_WIDTH
        idx = 0      # highlighted option
        top = 0      # first visible option 
        while True:
            try:
                height, width = stdscr.getmaxyx()
                box_width = min(width - 2,
                                max(len(title), max(len(o) for o in options)) + 8)
                box_height = min(height - 2, len(options) + 4)
                if box_height < min_h or box_width < min_w:
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
                pass    # a failed frame must never crash the program
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
    @staticmethod
    def _curses_show(stdscr, title, text):
        title_attr, _, _ = _init_curses_ui()
        min_h = StudentMarkManagement._MIN_VIEW_HEIGHT
        min_w = StudentMarkManagement._MIN_VIEW_WIDTH
        lines = text.splitlines() or ["(nothing to show)"]
        top = 0
        while True:
            height, width = stdscr.getmaxyx()
            visible = max(1, height - 3)
            try:
                if height < min_h or width < min_w:
                    _draw_too_small(stdscr, "Window too small. Enlarge it.")
                else:
                    top = max(0, min(top, len(lines) - visible))

                    stdscr.erase()
                    _safe_addstr(stdscr, 0, 0, f" {title} ".center(width, "="),
                                 curses.A_BOLD | title_attr)
                    for i, line in enumerate(lines[top:top + visible]):
                        _safe_addstr(stdscr, 2 + i, 2, line[:max(0, width - 4)])
                    _safe_addstr(stdscr, height - 1, 0,
                                 " Up/Down/PgUp/PgDn scroll   any other key: back "
                                 .center(width, "-"),
                                 curses.A_DIM)
                    stdscr.refresh()
            except curses.error:
                pass    # a failed frame must never crash the program
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
    @staticmethod
    def _capture_output(func, *args, **kwargs):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            func(*args, **kwargs)
        return buf.getvalue()
    def run(self):
        while True:
            choice_idx = curses.wrapper(self._curses_menu,
                                         "Student Mark Management", self.MENU_OPTIONS)
            if choice_idx is None or self.MENU_OPTIONS[choice_idx] == "Exit":
                print("Exiting program. Goodbye!")
                break
            label = self.MENU_OPTIONS[choice_idx]
            if label in self._DISPLAY_ONLY:
                method = getattr(self, self._DISPLAY_ONLY[label])
                text = self._capture_output(method)
                curses.wrapper(self._curses_show, label, text)
            else:
                method = getattr(self, self._INPUT_DRIVEN[label])
                print(f"\n== {label} ==")
                method()
                input("\nPress Enter to return to the menu...")
if __name__ == "__main__":
    StudentMarkManagement().run()