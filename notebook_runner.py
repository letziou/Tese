import papermill as pm

notebook_path = "ITC07.ipynb"
numbers = [12, 4, 9]

choice = sys.argv[1]
if choice.lower() == "all":
    for i in numbers:
        output_notebook = f"notebooks/notebook_set{i}.ipynb"
    
        params = {
            "input_file_path": f"datasets/exam_comp_set{i}.exam",
            "solution_file_path": f"solutions/notebook_solution_{i}.txt"
        }
        
        print(f"Running iteration {i} with parameters: {params}")
        
        pm.execute_notebook(notebook_path, output_notebook, parameters=params)
elif choice.lower().isdigit():
    output_notebook = f"notebooks/notebook_set{choice.lower()}.ipynb"
    
    params = {
        "input_file_path": f"datasets/exam_comp_set{choice.lower()}.exam",
        "solution_file_path": f"solutions/notebook_solution_{choice.lower()}.txt"
    }
    
    print(f"Running iteration {choice.lower()} with parameters: {params}")
    
    pm.execute_notebook(notebook_path, output_notebook, parameters=params)

else:
    output_notebook = f"notebooks/{choice.lower()}.ipynb"
    
    params = {
        "input_file_path": f"datasets/exam_{choice.lower()}.exam",
        "solution_file_path": f"solutions/notebook_solution_{choice.lower()}.txt"
    }
    
    print(f"Running iteration {choice.lower()} with parameters: {params}")
    
    pm.execute_notebook(notebook_path, output_notebook, parameters=params)