# Function to find 
def find_lines(filename, text):
    try:
        with open(filename, 'r') as file:
            for line in file:
                if text in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return int(parts[1])
        return None
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to find a specific line by the first word
def find_line_by_first_word(filename, first_word):
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith(first_word):
                    return line.strip().split(',')  # Return the full line as a string
        return None  # Return None if the line is not found
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

lines_file_path = '/home/letziou/5year/tese/data/exam_sets.txt'
input_file_path = '//home/letziou/5year/tese/datasets/exam_comp_set2.exam'  
output_file_path = '/home/letziou/5year/tese/data/exam_data.dat'

exam_start_line = 1
exam_lines = find_lines(lines_file_path, "Exams")
if exam_lines is not None:
    print(f"The lines of Exams are {exam_lines}")
else:
    print(f"Exams not found in the file.")


# Initialize lists to store exam data and a set for all students
exam_data = []
all_students = set()  # Use a set to avoid duplicates

with open(input_file_path, 'r') as file:
    lines = file.readlines()
    
# Step 2: Read the exam lines from the specified starting line
for index in range(exam_start_line, exam_start_line + exam_lines):
    if index < len(lines):  # Ensure we don't go out of bounds
        data_list = [int(x.strip()) for x in lines[index].split(',')]
        
        # Extract the duration and student IDs
        duration = data_list[0]
        student_ids = data_list[1:]
        size = len(student_ids)
        
        # Store the exam data
        exam_data.append((duration, student_ids, size))
        
        # Add student IDs to the global set
        all_students.update(student_ids)        

# Create AMPL formatted output
ampl_output = ""

# Define a set of exams
ampl_output += "set EXAMS := " + ' '.join([f'Exam_{index + 1}' for index in range(len(exam_data))]) + ';\n\n'

# Define a set of students
ampl_output += "set STUDENTS := " + ' '.join(map(str, all_students)) + ';\n\n'

ampl_output += f"param examSize :=\n"
for index, (duration, student_ids, size) in enumerate(exam_data):
    ampl_output += f"Exam_{index + 1} {size}\n"

# Define parameters for each exam duration
ampl_output += f"param examDuration :=\n"
for index, (duration, student_ids, size) in enumerate(exam_data):
    ampl_output += f"Exam_{index + 1} {duration}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n\n'
    
# Enrollment relation (0 or 1 indicating absence or presence)
ampl_output += "param enrolled (tr) :\n"

# Header row with exam names
ampl_output += ' '.join([f'Exam_{index + 1}' for index in range(len(exam_data))]) + " :=\n"

# Each row represents a student and their enrollment in each exam
for student_id in sorted(all_students):
    row = [f"{student_id}"]
    for index, (_, student_ids, size) in enumerate(exam_data):
        row.append("1" if student_id in student_ids else "0")
    ampl_output += ' '.join(row) + "\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n\n'

line_data = find_line_by_first_word(input_file_path, "FRONTLOAD")
values = int(line_data[1].strip())

ampl_output += f"param frontload :=\n"
for index, (duration, student_ids, size) in enumerate(exam_data):
    ampl_output += f"Exam_{index + 1} " + ("1\n" if size > values else "0\n")

ampl_output = ampl_output.rstrip('\n') + ' ;\n'

# Write to the AMPL .dat file
with open(output_file_path, 'w') as file:
    file.write(ampl_output)

print(f"Exams data file created at: {output_file_path}")
