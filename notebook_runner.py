import papermill as pm
import sys

notebook_path = "ITC07.ipynb"
numbers = [12]

choice = sys.argv[1].lower()

match choice:
    case "fcup-all":
        for i in numbers:
            output_notebook = f"notebooks/notebook_set{i}.ipynb"
            params = {
                "input_file_path": f"datasets/exam_comp_set{i}.exam",
                "solution_file_path": f"solutions/notebook_solution_{i}.txt"
            }
            print(f"Running iteration {i} with parameters: {params}")
            pm.execute_notebook(notebook_path, output_notebook, parameters=params)

        for j in range(1, 3):
            output_notebook = f"notebooks/fcup_set{j}.ipynb"
            params = {
                "input_file_path": f"fcup_instance/exam_fcup_set{j}.exam",
                "solution_file_path": f"solutions/fcup_notebook_solution_{j}.txt"
            }
            print(f"Running FCUP iteration {j} with parameters: {params}")
            pm.execute_notebook(notebook_path, output_notebook, parameters=params)

    case "all":
        for i in range(1, 13):
            output_notebook = f"notebooks/notebook_set{i}.ipynb"
            params = {
                "input_file_path": f"datasets/exam_comp_set{i}.exam",
                "solution_file_path": f"solutions/notebook_solution_{i}.txt"
            }
            print(f"Running iteration {i} with parameters: {params}")
            pm.execute_notebook(notebook_path, output_notebook, parameters=params)

    case "fcup":
        if len(sys.argv) < 3:
            print("Please specify a FCUP instance number or 'all'")
            sys.exit(1)

        number = sys.argv[2].lower()
        if number == "all":
            for i in range(1, 3):
                output_notebook = f"notebooks/fcup_set{i}.ipynb"
                params = {
                    "input_file_path": f"fcup_instance/exam_fcup_set{i}.exam",
                    "solution_file_path": f"solutions/fcup_notebook_solution_{i}.txt"
                }
                print(f"Running FCUP iteration {i} with parameters: {params}")
                pm.execute_notebook(notebook_path, output_notebook, parameters=params)
        else:
            output_notebook = f"notebooks/fcup_set{number}.ipynb"
            params = {
                "input_file_path": f"fcup_instance/exam_fcup_set{number}.exam",
                "solution_file_path": f"solutions/fcup_notebook_solution_{number}.txt"
            }
            print(f"Running FCUP iteration {number} with parameters: {params}")
            pm.execute_notebook(notebook_path, output_notebook, parameters=params)

    case _ if choice.isdigit():
        output_notebook = f"notebooks/notebook_set{choice}.ipynb"
        params = {
            "input_file_path": f"datasets/exam_comp_set{choice}.exam",
            "solution_file_path": f"solutions/notebook_solution_{choice}.txt"
        }
        print(f"Running iteration {choice} with parameters: {params}")
        pm.execute_notebook(notebook_path, output_notebook, parameters=params)

    case _:
        output_notebook = f"notebooks/{choice}.ipynb"
        params = {
            "input_file_path": f"datasets/exam_{choice}.exam",
            "solution_file_path": f"solutions/notebook_solution_{choice}.txt"
        }
        print(f"Running iteration {choice} with parameters: {params}")
        pm.execute_notebook(notebook_path, output_notebook, parameters=params)
