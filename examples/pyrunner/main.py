# main.py - runs in the browser via PyRunner (Pyodide)
print("PyRunner online")

def hello(name: str = "world") -> str:
    return f"Hello, {name}!"

print(hello("OpenComb"))

try:
    import numpy as np
    a = np.array([1, 2, 3])
    print("numpy sum:", int(a.sum()))
except Exception as e:
    print("numpy not loaded:", e)
