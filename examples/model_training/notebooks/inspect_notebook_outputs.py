import nbformat
import sys

def inspect_notebook(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        print(f"Inspecting notebook: {notebook_path}")
        for i, cell in enumerate(nb.cells):
            print(f"\n--- Cell {i+1} ({cell.cell_type}) ---")
            if cell.cell_type == 'code':
                print(f"Execution Count: {cell.execution_count}")
                print("Outputs:")
                for output in cell.outputs:
                    if output.output_type == 'stream':
                        print(output.text.encode('utf-8', 'replace').decode('utf-8'))
                    elif output.output_type == 'execute_result':
                        data = output.data.get('text/plain', '')
                        print(data.encode('utf-8', 'replace').decode('utf-8'))
                    elif output.output_type == 'display_data':
                        print("<Display Data (Image/Plot)>")
                    elif output.output_type == 'error':
                        print(f"Error: {output.ename}: {output.evalue}")
                        for line in output.traceback:
                            print(line)
    except Exception as e:
        print(f"Error reading notebook: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_notebook_outputs.py <notebook_path>")
    else:
        inspect_notebook(sys.argv[1])
