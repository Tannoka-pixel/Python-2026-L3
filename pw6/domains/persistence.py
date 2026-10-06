import os
import pickle
import gzip

DATA_FILE = "students.dat"

def save_data(students, courses, marks):
    data = {"students": students, "courses": courses, "marks": marks}
    with gzip.open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    with gzip.open(DATA_FILE, "rb") as f:
        return pickle.load(f)