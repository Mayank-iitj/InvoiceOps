import os
import sys

# Ensure working directory is the repository root containing 'backend'
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(script_dir, "backend")):
    root_dir = script_dir
elif os.path.exists(os.path.join(script_dir, "..", "backend")):
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
else:
    root_dir = script_dir

os.chdir(root_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("  Starting InvoiceOps Workbench & API Server")
    print(f"  Working Directory: {root_dir}")
    print("  URL: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("  Switch Room Blueprint: switch/invoiceops-room.template.yaml")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
