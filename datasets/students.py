import random

def generate_dataset(i, n):
    """
    Generates the first dataset as a list of numbers from i to n.
    
    Args:
    - i: Starting number of students
    - n: Total number of students.
    
    Returns:
    - A list of numbers representing a dataset of students.
    """
    if i < 1 or n < i:
        raise ValueError("The i number must be greater than or equal to 1 and n must be bigger than i.")
    return list(range(i, n))

def append_dataset(data, start, total_count, reuse_percentage):
    """
    Appends a second dataset with some reused numbers from the first dataset.
    
    Args:
    - data: The first dataset as a list of numbers.
    - start: The starting number for new students.
    - total_count: Total number of students in the second dataset.
    - reuse_percentage: Percentage of students to reuse from the first dataset.
    
    Returns:
    - A combined list of the first and second datasets.
    """
    # Calculate the number of reused students
    reuse_count = int(total_count * (reuse_percentage / 100))
    new_count = total_count - reuse_count

    # Randomly select students to reuse
    reused_students = random.sample(data, reuse_count)

    # Generate new students
    new_students = list(range(start, start + new_count))

    # Combine reused and new students
    second_dataset = reused_students + new_students

    # Shuffle the dataset to mix reused and new students
    random.shuffle(second_dataset)

    return sorted(second_dataset)

def combine_datasets(exclude_dataset, *datasets):
    """
    Combines multiple datasets into a single list without duplicates and removes IDs from the exclude_dataset.
    
    Args:
    - exclude_dataset: A list of IDs to exclude from the final combined dataset.
    - datasets: Variable number of lists to combine.
    
    Returns:
    - A combined list of all unique students, excluding IDs in exclude_dataset.
    """
    combined = set()
    for dataset in datasets:
        combined.update(dataset)
    
    # Remove IDs from the exclude_dataset
    combined.difference_update(exclude_dataset)
    
    return sorted(combined)

def write_to_file(filename, first_dataset, second_dataset, third_dataset, fourth_dataset, fifth_dataset):
    with open(filename, 'w') as file:
        file.write("Fifth year students Dataset:\n")
        file.write(", ".join(map(str, first_dataset)) + "\n\n")
        file.write("Fourth year students Dataset:\n")
        file.write(", ".join(map(str, second_dataset)) + "\n\n")
        file.write("Third year students Dataset:\n")
        file.write(", ".join(map(str, third_dataset)) + "\n\n")
        file.write("Second year students Dataset:\n")
        file.write(", ".join(map(str, fourth_dataset)) + "\n\n")
        file.write("First year students Dataset:\n")
        file.write(", ".join(map(str, fifth_dataset)) + "\n\n")

def write_to_stdout(first_dataset, second_dataset, third_dataset, fourth_dataset, fifth_dataset):
    print("Fifth year students Dataset:")
    print(", ".join(map(str, first_dataset)), "\n")
    print("Fourth year students Dataset:")
    print(", ".join(map(str, second_dataset)), "\n")
    print("Third year students Dataset:")
    print(", ".join(map(str, third_dataset)), "\n")
    print("Second year students Dataset:")
    print(", ".join(map(str, fourth_dataset)), "\n")
    print("First year students Dataset:")
    print(", ".join(map(str, fifth_dataset)), "\n")

try:
    n_students = 150

    # Generate students for fifth year
    fifth_dataset = generate_dataset(1, n_students)

    # Generate students for fourth year
    fourth_dataset = append_dataset(fifth_dataset, 150, n_students, 20)

    # Generate students for third year
    fourth_clean = combine_datasets(fifth_dataset, fourth_dataset)
    third_start = len(fourth_clean)
    third_dataset = append_dataset(fourth_clean, 300, n_students, 20)

    # Generate students for second year
    third_clean = combine_datasets(fourth_dataset, third_dataset)
    second_start = len(third_clean)
    second_dataset = append_dataset(third_clean, 450, n_students, 20)

    # Generate students for first year
    second_clean = combine_datasets(third_dataset, second_dataset)
    first_start = len(second_clean)
    first_dataset = append_dataset(second_clean, 600, n_students, 20)

    # Write all datasets to output file
    write_to_stdout(fifth_dataset, fourth_dataset, third_dataset, second_dataset, first_dataset)
    print(f"Datasets written.")

except ValueError as e:
    print(f"Error: {e}")