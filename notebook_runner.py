import papermill as pm

notebook_path = "ITC07.ipynb"

for i in range(1,13):
    output_notebook = f"comp_set{i}.ipynb"
    
    params = {
        "input_file_path": f"datasets/exam_comp_set{i}.exam",
        "solution_file_path": f"solutions/solution{i}.txt"
    }
    
    print(f"Running iteration {i} with parameters: {params}")
    
    pm.execute_notebook(notebook_path, output_notebook, parameters=params)
