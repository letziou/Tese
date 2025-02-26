import re

file_path = '/home/letziou/5year/tese/datasets/exam_comp_set2.exam'

size = {}

# Extracting information from file
with open(file_path, 'r') as file:
    lines = file.readlines()  # Read all lines at once for easier processing
    line_count = len(lines)
    
    i = 0
    while i < line_count:
        line = lines[i]
        
        # Using regex to capture bracket pair in order to extract to file
        matches = re.findall(r'\[(.*?):(.*?)\]', line)

        # Check for size
        if matches:
            for match in matches:
                word, value = match[0].strip(), match[1].strip() 
                size[word] = value
        else:
            if line.startswith('[') and line.endswith(']\n'):
                parameter_name = line[1:-2].strip()
                if parameter_name not in size:
                    # Counting lines until next parameter
                    count_lines = 0
                    j = i + 1
                    while j < line_count and not re.findall(r'\[(.*?)]', lines[j]):
                        count_lines += 1
                        j += 1
                    size[parameter_name] = count_lines
                    i = j - 1

        i += 1

# Writing to file
output_file_path = '/home/letziou/5year/tese/data/exam_sets.txt'
with open(output_file_path, 'w') as file:
    for param in size:
        file.write(f'{param} {size[param]}\n')

print("Set and size_of file created at:", output_file_path)
