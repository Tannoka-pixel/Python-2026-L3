import random
from abc import ABC, abstractmethod

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
    @abstractmethod
    def list(self):
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
    def list(self):
        print(f"{self.id:<12}{self.name:<30}{self.dob:<15}")
class Course(Entity):
    @classmethod
    def header(cls):
        return f"{'ID':<12}{'Name':<35}\n" + "-" * 47
    def list(self):
        print(f"{self.id:<12}{self.name:<35}")
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
        students = [Student(str(cls._START_ID), "Nguyen Khanh Hung", "8th Sep 2007")]
        for i in range(1, n):
            students.append(Student(str(cls._START_ID + i),
                                    cls._random_name(),
                                    cls._random_dob()))
        return students
class MarkBook:
    def __init__(self):
        self._marks = {}
    def set_mark(self, course_id, student_id, mark):
        self._marks.setdefault(course_id, {})[student_id] = float(mark)
    def get_course_marks(self, course_id):
        """Return a copy so callers cannot modify the internal data."""
        return dict(self._marks.get(course_id, {}))
    def has_marks(self, course_id):
        return bool(self._marks.get(course_id))
class StudentMarkManagement:
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
    def input_students(self):
        self._inpt_entities(Student, self._students, "student")
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
        for student in self._students:
            while True:
                raw = input(f"  Mark for {student.name} ({student.id}): ").strip()
                try:
                    mark = float(raw)
                    break
                except ValueError:
                    print("  Please enter a valid number.")
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
            self._marks.set_mark(course.id, student.id,
                                 round(random.uniform(low, high), 1))
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
    @staticmethod
    def _show_menu():
        print("\n===== Student Mark Management =====")
        print("1. Input Students (manual)")
        print("2. Generate Demo Students (140, random names)")
        print("3. Input Courses")
        print("4. Input Marks (manual)")
        print("5. Auto-generate Random Marks for a Course (15-18)")
        print("6. List Courses")
        print("7. List Students")
        print("8. Show Marks for a Course")
        print("0. Exit")
    def run(self):
        actions = {
            "1": self.input_students,
            "2": self.generate_demo_students,
            "3": self.input_courses,
            "4": self.input_marks,
            "5": self.generate_random_marks,
            "6": self.list_courses,
            "7": self.list_students,
            "8": self.show_marks,
        }
        while True:
            self._show_menu()
            choice = input("Enter your choice: ").strip()
            if choice == "0":
                print("Exiting program. Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice. Please try again.")
if __name__ == "__main__":
    StudentMarkManagement().run()