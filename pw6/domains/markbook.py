import math

class MarkBook:
    def __init__(self):
        self._marks = {}
    def _round_down(value):
        return math.floor(float(value) * 10) / 10
    def set_mark(self, course_id, student_id, mark):
        self._marks.setdefault(course_id, {})[student_id] = self._round_down(mark)
    def get_course_marks(self, course_id):
        return dict(self._marks.get(course_id, {}))
    def has_marks(self, course_id):
        return bool(self._marks.get(course_id))
