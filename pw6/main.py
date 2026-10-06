import random
import numpy as np
from domains import Student, Course, MarkBook, DemoStudentFactory
from input import (read_int, read_mark,
                    input_student_details, input_course_details)
from output import show_menu, show_text, capture_output
from persistence import save_data, load_data

class StudentMarkManagement:
    MENU_OPTIONS = [
        "Input Students (manual)",
        "Generate Demo Students (140, random names)",
        "Input Courses",
        "Input Marks (manual)",
        "Auto-generate Random Marks for a Course (15-18)",
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
        "Auto-generate Random Marks for a Course (15-18)": "generate_random_marks",
        "Show Marks for a Course": "show_marks",
        "Show GPA for a Student": "show_gpa",
    }
    _DISPLAY_ONLY = {
        "List Courses": "list_courses",
        "List Students": "list_students",
        "Sort & Show Students by GPA (Descending)": "sort_students_by_gpa",
    }

    def __init__(self):
        self._students = []          # list of Student
        self._courses = []           # list of Course
        self._marks = MarkBook()

        data = load_data()
        if data is not None:
            self._students = data["students"]
            self._courses = data["courses"]
            self._marks = data["marks"]
            print("Loaded saved data from students.dat.")
        
    @staticmethod
    def _find(collection, entity_id):
        """Polymorphic lookup: works for both Students and Courses."""
        for item in collection:
            if item.id == entity_id:
                return item
        return None

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
        """Weighted average of marks by course credits, using numpy arrays."""
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
        n = read_int("Enter number of students to add: ")
        for _ in range(n):
            print(f"\nStudent {len(self._students) + 1}:")
            s = Student()
            input_student_details(s)
            self._students.append(s)

    def generate_demo_students(self, n=140):
        self._students = DemoStudentFactory.create(n)
        print(f"Generated {n} demo students.")

    def input_courses(self):
        n = read_int("Enter number of courses to add: ")
        for _ in range(n):
            print(f"\nCourse {len(self._courses) + 1}:")
            c = Course()
            input_course_details(c)
            self._courses.append(c)

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
            mark = read_mark(f"  Mark for {student.name} ({student.id}): ")
            self._marks.set_mark(course.id, student.id, mark)

    def generate_random_marks(self, low=15.0, high=18.0):
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
        print("\n--- Courses List ---")
        if not self._courses:
            print("No courses available.")
            return
        print(Course.header())
        for c in self._courses:
            c.list()

    def list_students(self):
        print("\n--- Students List ---")
        if not self._students:
            print("No students available.")
            return
        print(Student.header())
        for s in self._students:
            s.list()

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
        
    def run(self):
        while True:
            choice_idx = show_menu("Student Mark Management", self.MENU_OPTIONS)
            if choice_idx is None or self.MENU_OPTIONS[choice_idx] == "Exit":
                print("Exiting program. Goodbye!")
                break
            label = self.MENU_OPTIONS[choice_idx]
            if label in self._DISPLAY_ONLY:
                method = getattr(self, self._DISPLAY_ONLY[label])
                show_text(label, capture_output(method))
            else:
                method = getattr(self, self._INPUT_DRIVEN[label])
                print(f"\n== {label} ==")
                method()
                input("\nPress Enter to return to the menu...")

        save_data(self._students, self._courses, self._marks)
        print("Data saved to students.dat.")

if __name__ == "__main__":
    StudentMarkManagement().run()
