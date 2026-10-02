from domains.entity import Entity

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

    @classmethod
    def header(cls):
        return f"{'ID':<12}{'Name':<30}{'Credit':<10}\n" + "-" * 52

    def row(self):
        return f"{self.id:<12}{self.name:<30}{self.credit:<10.1f}"
