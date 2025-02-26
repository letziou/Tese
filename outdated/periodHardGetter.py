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
output_file_path = '/home/letziou/5year/tese/data/periodHard_data.dat'

exam_lines = find_lines(lines_file_path, "Exams")
period_lines = find_lines(lines_file_path, "Periods")
room_lines = find_lines(lines_file_path, "Rooms")
periodHard_lines = find_lines(lines_file_path, "PeriodHardConstraints")
periodHard_start_line = 4 + exam_lines + period_lines + room_lines

if periodHard_lines is not None:
    print(f"The lines of PerioHardConstraint are {periodHard_lines}")
else:
    print(f"PerioHardConstraint not found in the file.")

periodHard_data = []

with open(input_file_path, "r") as file:
    lines = file.readlines()

for index in range(periodHard_start_line, periodHard_start_line + periodHard_lines):
    if index < len(lines):
        line_data = lines[index].split(',')
        fExam = int(line_data[0].strip())
        operation = line_data[1].strip()
        sExam = int(line_data[2].split())    

        periodHard_data.append((fExam, operation, sExam))

# O que é o SET ?
# como representar os valores