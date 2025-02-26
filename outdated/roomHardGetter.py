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

lines_file_path = '/home/letziou/5year/tese/data/exam_sets.txt'
input_file_path = '//home/letziou/5year/tese/datasets/exam_comp_set2.exam'  
output_file_path = '/home/letziou/5year/tese/data/exam_data.dat'

exam_lines = find_lines(lines_file_path, "Exams")
period_lines = find_lines(lines_file_path, "Periods")
room_lines = find_lines(lines_file_path, "Rooms")
periodHard_lines = find_lines(lines_file_path, "PeriodHardConstraints")
roomHard_lines = find_lines(lines_file_path, "RoomHardConstraints")
roomHard_start_line = 5 + exam_lines + period_lines + room_lines + periodHard_lines

if roomHard_lines is not None:
    print(f"The lines of RoomHardConstraints are {roomHard_lines}")
else:
    print(f"RoomHardConstraints not found in file")

roomHard_data = []

with open(input_file_path, "r") as file:
    lines = file.readlines()

for index in range(roomHard_start_line, roomHard_start_line + roomHard_lines):
    if index < len(lines):
        line_data = lines[index].split(',')
        exam = line_data[0].strip()

        roomHard_data.append(exam)

# Defining parameter roomExclusive
ampl_output = "\nparam roomExclusive :=\n"

for exam in roomHard_data:
    ampl_output += f"Exam_{exam}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n'    

# Write to the output file
with open(output_file_path, 'a') as file:
    file.write(ampl_output)

print(f"RoomHardConstraint data file created at: {output_file_path}")