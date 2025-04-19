import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(file), '..'))
print(f"Adding {project_root} to Python path")
sys.path.insert(0, project_root) 
