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
output_file_path = '/home/letziou/5year/tese/data/room_data.dat'

exam_lines = find_lines(lines_file_path, "Exams")
period_lines = find_lines(lines_file_path, "Periods")
room_lines = find_lines(lines_file_path, "Rooms")
room_start_line = 3 + exam_lines + period_lines

if room_lines is not None:
    print(f"The lines of Rooms are {room_lines}")
else:
    print(f"Rooms not found in the file.")

room_data = []

with open(input_file_path, "r") as file:
    lines = file.readlines()

for index in range(room_start_line, room_start_line + room_lines):
    if index < len(lines):
        line_data = lines[index].split(',')
        size = int(line_data[0].strip())
        penalty = int(line_data[1].strip())

        room_data.append((size, penalty))

ampl_output = ""

ampl_output += "set ROOMS := " + ' '.join([f'Room_{index + 1}' for index in range(len(room_data))]) + ";\n\n"

# Defining parameter roomsize
ampl_output += f"param roomSize :=\n"

for index, (size, penalty) in enumerate(room_data):
    ampl_output += f"Room_{index + 1} {size}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n\n'    

# Defining parameter roomPenalty
ampl_output += f"param roomPenalty :=\n"

for index, (size, penalty) in enumerate(room_data):
    ampl_output += f"Room_{index + 1} {penalty}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n'

# Write to the output file
with open(output_file_path, 'w') as file:
    file.write(ampl_output)

print(f"Room data file created at: {output_file_path}")