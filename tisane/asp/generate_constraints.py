"""MOVED THIS TO THE KNOWLEDGE_BASE CLASS - Dec. 18, 2020"""
import os 
import re 

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

def main(): 
    with open('constraints.lp', 'r') as generic_constraints, open('specific_constraints.lp', 'w') as specific_constraints: 
            
            for line in generic_constraints.lines(): 
               pass 


if __name__ == "__main__": 
    main()