import os
import sys

# Ensure root directory containing 'backend' is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))

# If script is inside 'backend/', the repository root is parent directory
if os.path.basename(script_dir) == "backend":
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
elif os.path.exists(os.path.join(script_dir, "backend")):
    root_dir = script_dir
else:
    root_dir = script_dir

os.chdir(root_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print("  Starting InvoiceOps Workbench & API Server")
    print(f"  Working Directory: {root_dir}")
    print(f"  URL: http://{host}:{port}")
    print(f"  API Docs: http://{host}:{port}/docs")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
