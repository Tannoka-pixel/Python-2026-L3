from domains.entity import Entity

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

    @classmethod
    def header(cls):
        return f"{'ID':<12}{'Name':<30}{'DoB':<15}\n" + "-" * 57

    def row(self):
        return f"{self.id:<12}{self.name:<30}{self.dob:<15}"
