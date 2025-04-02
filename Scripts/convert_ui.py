import os
import subprocess

ui_design_dir = os.path.join(os.getcwd(), "ui_design_files")
ui_files_dir = os.path.join(os.getcwd(), "ui_files")

if not os.path.exists(ui_design_dir):
    print(f"Error: ui_design_files directory not found at {ui_design_dir}")
    exit(1)

# Create ui_files directory if it doesn't exist
if not os.path.exists(ui_files_dir):
    try:
        os.makedirs(ui_files_dir)
        print(f"Created directory: {ui_files_dir}")
    except OSError as e:
        print(f"Error creating ui_files directory: {e}")
        exit(1)

for filename in os.listdir(ui_design_dir):
    if filename.endswith(".ui"):
        ui_filepath = os.path.join(ui_design_dir, filename)
        output_filename = filename.replace(".ui", "_ui.py")
        output_filepath = os.path.join(ui_files_dir, output_filename)

        print(f"Converting {ui_filepath} to {output_filepath}")
        try:
            subprocess.run(
                ["pyuic5", ui_filepath, "-o", output_filepath],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error converting {ui_filepath}:")
            print(e.stderr)
            exit(1)

print("Conversion complete.")
