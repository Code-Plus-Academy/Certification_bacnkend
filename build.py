import os
import shutil
import subprocess

print("=== Starting Netlify Build Automation ===")

functions_dir = os.path.abspath("netlify/functions")
os.makedirs(functions_dir, exist_ok=True)

# 1. Install all pip requirements directly into netlify/functions
print("[1/3] Installing dependencies into netlify/functions/...")
req_file = os.path.abspath("requirements.txt")
subprocess.run(["pip", "install", "-r", req_file, "-t", functions_dir], check=True)

# 2. Copy root Python modules into netlify/functions (app.py -> main_app.py to preserve handler)
print("[2/3] Copying Python modules to netlify/functions/...")
shutil.copy("app.py", os.path.join(functions_dir, "main_app.py"))
for fname in ["generator.py", "cloud_uploader.py"]:
    if os.path.exists(fname):
        shutil.copy(fname, os.path.join(functions_dir, fname))

# 3. Copy templates directory into netlify/functions
print("[3/3] Copying templates folder to netlify/functions/...")
templates_src = os.path.abspath("templates")
templates_dst = os.path.join(functions_dir, "templates")
if os.path.exists(templates_src):
    if os.path.exists(templates_dst):
        shutil.rmtree(templates_dst)
    shutil.copytree(templates_src, templates_dst)

print("=== Netlify Build Automation Completed Successfully ===")
