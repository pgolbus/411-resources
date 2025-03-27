import sys
import os

# Get the absolute path to the directory containing the boxing package
#because what the crap is wrong with the file path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"Adding {project_root} to Python path")
sys.path.insert(0, project_root)