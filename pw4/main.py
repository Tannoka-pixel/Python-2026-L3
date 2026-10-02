import numpy as np
from domains import Student, Course, MarkBook
from input import read_int, input_student_details, input_course_details
from output import text_menu, text_show, capture_output

class StudentMarkManagement:
    MENU_OPTIONS = [
        "Input Students (manual)",
        "Input Courses",
        "List Courses",
        "List Students",
        "Exit",
    ]

    def __init__(self):
        self._students = []
        self._courses = []
        self._marks = MarkBook()

    def input_students(self):
        n = read_int("Enter number of students to add: ")
        for _ in range(n):
            print(f"\nStudent {len(self._students) + 1}:")
            s = Student()
            input_student_details(s)
            self._students.append(s)

    def input_courses(self):
        n = read_int("Enter number of courses to add: ")
        for _ in range(n):
            print(f"\nCourse {len(self._courses) + 1}:")
            c = Course()
            input_course_details(c)
            self._courses.append(c)

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

    def run(self):
        while True:
            choice_idx = text_menu("Student Mark Management", self.MENU_OPTIONS)
            if choice_idx is None or self.MENU_OPTIONS[choice_idx] == "Exit":
                print("Exiting program. Goodbye!")
                break

            label = self.MENU_OPTIONS[choice_idx]
            if label == "Input Students (manual)":
                self.input_students()
            elif label == "Input Courses":
                self.input_courses()
            elif label == "List Courses":
                text = capture_output(self.list_courses)
                text_show(label, text)
            elif label == "List Students":
                text = capture_output(self.list_students)
                text_show(label, text)

if __name__ == "__main__":
    StudentMarkManagement().run()
