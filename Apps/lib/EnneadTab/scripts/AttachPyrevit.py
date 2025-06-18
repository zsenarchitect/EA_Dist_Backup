import subprocess

def attach_pyrevit_all():
    """Attach pyRevit to all installed Revit versions using the recommended CLI command."""
    pyrevit_cmd = ["pyrevit", "attach", "master", "default", "--installed"]
    try:
        result = subprocess.run(pyrevit_cmd, capture_output=True, text=True, check=True)
        print(f"[SUCCESS] pyRevit attached to all installed Revit versions:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to attach pyRevit:\n{e.stderr}")
        print("[DEBUG] This may be due to an incompatible minimal version of pyRevit.")
        check_multiple_pyrevit_versions()

def check_multiple_pyrevit_versions():
    """Check if multiple versions of pyRevit are installed and print them."""
    try:
        env_cmd = ["pyrevit", "env"]
        result = subprocess.run(env_cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        version_lines = [line for line in lines if "pyRevit CLI" in line or "pyRevit" in line and "Version" in line]
        if len(version_lines) > 1:
            print("[WARNING] Multiple versions of pyRevit detected:")
            for vline in version_lines:
                print(f"  - {vline.strip()}")
            print("[SUGGESTION] Please ensure only one version of pyRevit is set as default or available in PATH.")
        elif version_lines:
            print(f"[INFO] Detected pyRevit version: {version_lines[0].strip()}")
        else:
            print("[INFO] Could not detect any pyRevit version from 'pyrevit env'.")
    except Exception as ex:
        print(f"[ERROR] Could not check pyRevit versions: {ex}")

if __name__ == "__main__":
    attach_pyrevit_all()
