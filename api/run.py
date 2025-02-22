#! /usr/bin/env python

if __name__ == '__main__':
    import os
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.system(f"fastapi dev {cwd}/api.py")   # Start the FastAPI server