def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")

def ask_input(prompt, setter):
    while True:
        try:
            setter(input(prompt))
            return
        except ValueError as err:
            print(f"  {err}")

def input_student_details(student):
    ask_input("  ID: ", lambda v: setattr(student, "id", v))
    ask_input("  Name: ", lambda v: setattr(student, "name", v))
    ask_input("  Date of Birth (dd/mm/yyyy): ", lambda v: setattr(student, "dob", v))

def input_course_details(course):
    ask_input("  ID: ", lambda v: setattr(course, "id", v))
    ask_input("  Name: ", lambda v: setattr(course, "name", v))
    ask_input("  Credit: ", lambda v: setattr(course, "credit", v))
