import random

from domains.student import Student

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

    def _ordinal(n):
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
    def _random_name(cls):
        return (f"{random.choice(cls._SURNAMES)} "
                f"{random.choice(cls._MIDDLE_NAMES)} "
                f"{random.choice(cls._GIVEN_NAMES)}")
    def _random_dob(cls, start_year=2005, end_year=2008):
        day = random.randint(1, 28)
        month = random.choice(cls._MONTHS)
        year = random.randint(start_year, end_year)
        return f"{cls._ordinal(day)} {month} {year}"
    def create(cls, n=140):
        students = [Student(str(cls._START_ID), "Nguyen Khanh Hung", "8th Sep 2007")]
        for i in range(1, n):
            students.append(Student(str(cls._START_ID + i),
                                    cls._random_name(),
                                    cls._random_dob()))
        return students
