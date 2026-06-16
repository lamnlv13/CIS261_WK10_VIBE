# Luis Macias
# CIS261
# VIBE Coding

import os
import sys
import termios
import tty
from typing import Dict, List, Optional

DATA_FILE = "student_grades.txt"

class Student:
    def __init__(self, student_id: str, name: str, scores: List[float]) -> None:
        self.student_id = student_id.strip()
        self.name = name.strip()
        if len(scores) != 3:
            raise ValueError("Exactly three test scores are required.")
        for score in scores:
            if score < 0 or score > 100:
                raise ValueError("Each score must be between 0 and 100.")
        self.scores = [float(score) for score in scores]
        self.average = sum(self.scores) / 3.0
        if self.average >= 90:
            self.grade = "A"
        elif self.average >= 80:
            self.grade = "B"
        elif self.average >= 70:
            self.grade = "C"
        elif self.average >= 60:
            self.grade = "D"
        else:
            self.grade = "F"

    def to_line(self) -> str:
        return (
            f"{self.name}|{self.student_id}|{self.scores[0]:.2f}|{self.scores[1]:.2f}|{self.scores[2]:.2f}|{self.average:.2f}|{self.grade}\n"
        )

    @staticmethod
    def from_line(line: str) -> Optional["Student"]:
        parts = line.strip().split("|")
        if len(parts) != 7:
            return None
        if parts[0] == "name":
            return None
        try:
            student = Student(parts[1], parts[0], [float(parts[2]), float(parts[3]), float(parts[4])])
            return student
        except ValueError:
            return None

    def __str__(self) -> str:
        return (
            f"ID: {self.student_id}\n"
            f"Name: {self.name}\n"
            f"Test 1: {self.scores[0]:.2f}\n"
            f"Test 2: {self.scores[1]:.2f}\n"
            f"Test 3: {self.scores[2]:.2f}\n"
            f"Average: {self.average:.2f}\n"
            f"Grade: {self.grade}"
        )

class StudentManager:
    def __init__(self) -> None:
        self.records: Dict[str, Student] = {}
        self.load_records()

    def add_student(self, student_id: str, name: str, scores: List[float]) -> Student:
        if student_id in self.records:
            raise ValueError(f"Student ID '{student_id}' already exists.")
        student = Student(student_id, name, scores)
        self.records[student_id] = student
        return student

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.records.get(student_id)

    def remove_student(self, student_id: str) -> bool:
        return self.records.pop(student_id, None) is not None

    def list_students(self) -> List[Student]:
        return sorted(self.records.values(), key=lambda rec: rec.student_id)

    def save_records(self) -> None:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                file.write("name|id|test1|test2|test3|average|grade\n")
                for record in self.records.values():
                    file.write(record.to_line())
        except OSError as exc:
            print(f"Error saving records to '{DATA_FILE}': {exc}")

    def load_records(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    student = Student.from_line(line)
                    if student is not None:
                        self.records[student.student_id] = student
        except OSError as exc:
            print(f"Error loading records from '{DATA_FILE}': {exc}")


def prompt(prompt_text: str) -> str:
    try:
        return input(prompt_text).strip()
    except EOFError:
        return ""


def get_single_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def prompt_score(index: int) -> float:
    while True:
        try:
            raw = prompt(f"Enter score {index} (0-100): ")
            if raw == "\x1b":
                raise KeyboardInterrupt
            score = float(raw)
            if 0 <= score <= 100:
                return score
            print("Score must be between 0 and 100.")
        except ValueError:
            print("Invalid score. Please enter a number.")


def add_student_flow(manager: StudentManager) -> None:
    try:
        student_id = prompt("Student ID: ")
        if student_id == "\x1b":
            print("Add student cancelled.")
            return
        name = prompt("Student name: ")
        if name == "\x1b":
            print("Add student cancelled.")
            return
        scores = [prompt_score(i) for i in range(1, 4)]
        manager.add_student(student_id, name, scores)
        print(f"Student {name} ({student_id}) added successfully.")
    except ValueError as exc:
        print(f"Input error: {exc}")
    except KeyboardInterrupt:
        print("Input cancelled. Returning to main menu.")


def show_student_flow(manager: StudentManager) -> None:
    student_id = prompt("Student ID: ")
    if student_id == "\x1b":
        print("Show student cancelled.")
        return
    student = manager.get_student(student_id)
    if student is None:
        print(f"No student found with ID '{student_id}'.")
    else:
        print("\n" + str(student))


def search_student_flow(manager: StudentManager) -> None:
    search_name = prompt("Enter name to search: ")
    if search_name == "\x1b":
        print("Search cancelled.")
        return
    matches = [
        student
        for student in manager.list_students()
        if search_name.lower() in student.name.lower()
    ]
    if not matches:
        print(f"No students found matching '{search_name}'.")
        return
    print_table_header()
    for student in matches:
        print_student_row(student)


def remove_student_flow(manager: StudentManager) -> None:
    student_id = prompt("Student ID to remove: ")
    if student_id == "\x1b":
        print("Remove student cancelled.")
        return
    if manager.remove_student(student_id):
        print(f"Student {student_id} removed.")
    else:
        print(f"No student found with ID '{student_id}'.")


def save_records_flow(manager: StudentManager) -> None:
    manager.save_records()
    print(f"Records saved to '{DATA_FILE}'.")


def print_menu() -> None:
    print("\nStudent Record Manager")
    print("1. Add student")
    print("2. Show student record")
    print("3. Show all students")
    print("4. Search student by name")
    print("5. Remove student")
    print("6. Save records")
    print("7. Exit")
    print("Press ESC at the menu to exit immediately.")


def get_menu_choice() -> str:
    print("Choose an option [1-7] or press ESC to exit: ", end="", flush=True)
    choice = get_single_key()
    print()
    if choice == "\x1b":
        return "ESC"
    return choice


def print_table_header() -> None:
    print(
        f"{'ID':<10} {'Name':<20} {'Test1':>6} {'Test2':>6} {'Test3':>6} {'Avg':>6} {'Grade':>6}"
    )
    print("-" * 62)


def print_student_row(student: Student) -> None:
    print(
        f"{student.student_id:<10} {student.name:<20} {student.scores[0]:>6.2f} {student.scores[1]:>6.2f} {student.scores[2]:>6.2f} {student.average:>6.2f} {student.grade:>6}"
    )


def display_all_students(manager: StudentManager) -> None:
    students = manager.list_students()
    if not students:
        print("No student records available.")
        return
    print_table_header()
    for student in students:
        print_student_row(student)
    averages = [student.average for student in students]
    best = max(students, key=lambda s: s.average)
    worst = min(students, key=lambda s: s.average)
    class_avg = sum(averages) / len(averages)
    print("\nClass statistics:")
    print(f"  Highest average: {best.average:.2f} ({best.name}, {best.student_id})")
    print(f"  Lowest average:  {worst.average:.2f} ({worst.name}, {worst.student_id})")
    print(f"  Class average:   {class_avg:.2f}")


def main() -> None:
    manager = StudentManager()
    print("Welcome to the student record manager.")

    while True:
        print_menu()
        choice = get_menu_choice()

        if choice == "ESC" or choice == "7":
            manager.save_records()
            print("Records saved. Goodbye!")
            break

        if choice == "1":
            add_student_flow(manager)

        elif choice == "2":
            show_student_flow(manager)

        elif choice == "3":
            display_all_students(manager)

        elif choice == "4":
            search_student_flow(manager)

        elif choice == "5":
            remove_student_flow(manager)

        elif choice == "6":
            save_records_flow(manager)

        else:
            print("Invalid option. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
