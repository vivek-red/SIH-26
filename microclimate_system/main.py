import subprocess
import sys
import os

def get_python_exec():
    # Try to use the local virtual environment Python if it exists
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

def main():
    py_exec = get_python_exec()
    print("=== Step 1: Data Ingestion ===")
    subprocess.run([py_exec, "data_ingestion.py"], check=True)
    
    print("\n=== Step 2: Preprocessing ===")
    subprocess.run([py_exec, "preprocessing.py"], check=True)
    
    print("\n=== Step 3: Model Training ===")
    subprocess.run([py_exec, "train_model.py"], check=True)
    
    print("\n=== Step 4: Real-Time Inference ===")
    subprocess.run([py_exec, "inference.py"], check=True)
    
    print("\n=== Step 5: Alert Layer ===")
    subprocess.run([py_exec, "alert_layer.py"], check=True)

if __name__ == "__main__":
    main()
