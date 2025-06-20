import csv
import sys
import pandas as pd
from collections import defaultdict

def organizing_by_course(file_path):
    exams = defaultdict(list)

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            next(csv_reader, None)      # Line to skip the header of csv

            for row in csv_reader:
                if len(row) >= 2:
                    student_id = row[0].strip() 
                    course_id = row[1].strip()

                    exams[course_id].append(student_id)

    except FileNotFoundError:
        print(f"Error file {file_path} not found.")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}
    
    return dict(exams)  

def file_print_exams(exams, file_path):
    with open(file_path, "w") as file:
        for course_id, students in exams.items():
            exam_number = course_id.split('_')[-1] if '_' in course_id else course_id
            course_time = 120
            
            student_numbers = []
            for student_id in students:
                if '_' in student_id:
                    numeric_part = student_id.split('_')[-1]
                    student_numbers.append(numeric_part)
                else:
                    student_numbers.append(student_id)
            
            student_numbers.sort(key=lambda x: int(x))
            
            file.write(f"{exam_number}, {course_time}, {', '.join(student_numbers)}\n")

def room_capacities(file_path):
    try:
        df = pd.read_excel(file_path, engine='xlrd')
        rooms = {}

        for index, row in df.iterrows():
            room_number = str(row.iloc[2]).strip()
            capacity = row.iloc[4]
            
            if isinstance(capacity, str) and '|' in capacity:      # Handles "24 | 16" case
                capacity = capacity.split('|')[0].strip()
            
            try:
                capacity = int(float(capacity))
                rooms[room_number] = capacity
            except (ValueError, TypeError):
                print(f"Warning: Could not parse capacity for room {room_number}: {capacity}")
        
        return rooms
    
    except FileNotFoundError:
        print(f"Error file {file_path} not found.")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}

def file_print_rooms(rooms, file_path):
    with open(file_path, "w") as file:
        for room, capacity in rooms.items():
            file.write(f"{room}, {capacity}, 0\n")

def print_statistics(exams, rooms, semester):
    all_students = set()
    for students in exams.values():
        all_students.update(students)
        
    num_exams = len(exams)
    num_rooms = len(rooms)
    
    print(f"\n=== Statistics for Semester {semester} ===")
    print(f"Number of different students: {len(all_students)}")
    print(f"Number of exams: {num_exams}")
    print(f"Number of rooms: {num_rooms}")

if __name__ == "__main__":
    choice = sys.argv[1]
    if choice.lower() == "1":
        csv_file_path = "./fcup_instance/anonymized_S1.csv"
        semester = 1
    else:
        csv_file_path = "./fcup_instance/anonymized_S2.csv"
        semester = 2
    
    # Organize students by course
    exams = organizing_by_course(csv_file_path)
    
    #if exams:
    #    if choice.lower() == "1": file_print_exams(exams, "./fcup_instance/studentsS1.txt")
    #    else: file_print_exams(exams, "./fcup_instance/studentsS2.txt")
    #else: print("No data could be processed.")

    rooms = room_capacities("./fcup_instance/salas_exames_12jun2025.xls")
    #file_print_rooms(rooms, "./fcup_instance/rooms.txt")

    if exams and rooms:
        print_statistics(exams, rooms, semester)