import csv
import os
import zipfile

from domains import Student, Course

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.txt")
COURSES_FILE = os.path.join(BASE_DIR, "courses.txt")
MARKS_FILE = os.path.join(BASE_DIR, "marks.txt")
DATA_FILE = os.path.join(BASE_DIR, "students.dat")
_TEXT_FILES = (STUDENTS_FILE, COURSES_FILE, MARKS_FILE)
def _write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
def save_students(students):
    _write_rows(STUDENTS_FILE, ([s.id, s.name, s.dob] for s in students))
def save_courses(courses):
    _write_rows(COURSES_FILE, ([c.id, c.name, c.credit] for c in courses))
def save_marks(courses, markbook):
    rows = []
    for course in courses:
        for student_id, mark in markbook.get_course_marks(course.id).items():
            rows.append([course.id, student_id, mark])
    _write_rows(MARKS_FILE, rows)
def compress_data():
    existing = [p for p in _TEXT_FILES if os.path.exists(p)]
    if not existing:
        return False
    with zipfile.ZipFile(DATA_FILE, "w", zipfile.ZIP_DEFLATED) as z:
        for path in existing:
            z.write(path, arcname=os.path.basename(path))
    return True
def decompress_data()
    if not os.path.exists(DATA_FILE):
        return False
    with zipfile.ZipFile(DATA_FILE) as z:
        names = z.namelist()
        for path in _TEXT_FILES:
            name = os.path.basename(path)
            if name in names:
                z.extract(name, BASE_DIR)
    return True
def _read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f) if row]
def load_students():
    return [Student(sid, name, dob) for sid, name, dob in _read_rows(STUDENTS_FILE)]
def load_courses():
    return [Course(cid, name, credit) for cid, name, credit in _read_rows(COURSES_FILE)]
def load_marks(markbook):
    for course_id, student_id, mark in _read_rows(MARKS_FILE):
        markbook.set_mark(course_id, student_id, mark)
