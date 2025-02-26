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
output_file_path = '/home/letziou/5year/tese/data/weight_data.dat'

exam_lines = find_lines(lines_file_path, "Exams")
period_lines = find_lines(lines_file_path, "Periods")
room_lines = find_lines(lines_file_path, "Rooms")
periodHard_lines = find_lines(lines_file_path, "PeriodHardConstraints")
roomHard_lines = find_lines(lines_file_path, "RoomHardConstraints")
weight_lines = find_lines(lines_file_path, "InstitutionalWeightings")
weight_start_line = 6 + exam_lines + period_lines + room_lines + periodHard_lines + roomHard_lines

if weight_lines is not None:
    print(f"The lines of InstitutionalWeightings are {weight_lines}")
else:
    print(f"InstitutionalWeightings not found in file")

weight_data = []

with open(input_file_path, "r") as file:
    lines = file.readlines()

for index in range(weight_start_line, weight_start_line + weight_lines):
    if index < len(lines):
        line_data = lines[index].strip().split(',')

        key = line_data[0].strip()
        values = int(line_data[1].strip())

        if key != "FRONTLOAD":
            weight_data.append((key, values)) if values else None

ampl_output = "set PARAMETERS := " + ' '.join([f'{param}' for (param, weight) in weight_data]) + ';\n\n'

ampl_output += "param weights :=\n"
for (param, weight) in weight_data:
    ampl_output += f"{param} {weight}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n'

# Write to the AMPL .dat file
with open(output_file_path, 'w') as file:
    file.write(ampl_output)

print(f"InstitutionalWeightings data file created at: {output_file_path}")