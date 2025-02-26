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
output_file_path = '/home/letziou/5year/tese/data/period_data.dat'

exam_lines = find_lines(lines_file_path, "Exams")
period_lines = find_lines(lines_file_path, "Periods")
period_start_line = 2 + exam_lines

if period_lines is not None:
    print(f"The lines of Periods are {period_lines}")
else:
    print(f"Periods not found in the file.")

# Initialize lists to store period data
period_data = []
period_dates = []

# Read the input file to extract the period data
with open(input_file_path, 'r') as file:
    lines = file.readlines()

# Process each line in the Periods section to get time and penalty
for index in range(period_start_line, period_start_line + period_lines):
    if index < len(lines):  # Ensure we don't go out of bounds
        # Extract the time (third element) and penalty (fourth element)
        line_data = lines[index].split(',')
        date = line_data[0].strip() 
        time = int(line_data[2].strip())        # Third element
        penalty = int(line_data[3].strip())     # Fourth element
        
        # Store the extracted data in a tuple
        period_dates.append(date)
        period_data.append((time, penalty))

# Create AMPL formatted output
ampl_output = ""

# Define a set of exams
ampl_output += "set PERIODS := " + ' '.join([f'Period_{index + 1}' for index in range(len(period_data))]) + ';\n\n'

# Define duration
ampl_output += f"param periodDuration :=\n"
for index, (time, penalty) in enumerate(period_data):
    ampl_output += f"Period_{index + 1} {time}\n"

ampl_output = ampl_output.rstrip('\n') + ' ;\n\n'    

# Define penalty
ampl_output += f"param periodPenalty :=\n"
for index, (time, penalty) in enumerate(period_data):
    ampl_output += f"Period_{index + 1} {penalty}\n"    

ampl_output = ampl_output.rstrip('\n') + ' ;\n\n'

# Define the same-day matrix
ampl_output += "param sameDay (tr) :\n" + ' '.join([f'Period_{i + 1}' for i in range(len(period_data))]) + " :=\n"

# Populate the matrix with 1 if two periods are on the same date, 0 otherwise
for i in range(len(period_dates)):
    row = [f"Period_{i + 1}"]
    for j in range(len(period_dates)):
        row.append("1" if period_dates[i] == period_dates[j] else "0")
    ampl_output += ' '.join(row) + "\n"

# Write to the output file
with open(output_file_path, 'w') as file:
    file.write(ampl_output)

print(f"Period data file created at: {output_file_path}")

