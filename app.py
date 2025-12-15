import os
import shutil
import zipfile
from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Import the core logic (your Tree Data Structure and Algorithm)
from sorter import Sorter

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Create a temporary directory for file processing
UPLOAD_FOLDER = "./temp_uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Helper Functions ---


def package_sorted_directory(source_dir, output_zip_path):
    """
    Creates a ZIP file containing the sorted directory structure.
    """
    # Use 'w' mode to create a new zip file
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # os.walk traverses the directory tree
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)

                # Create a relative path for the file inside the ZIP.
                # This ensures the ZIP extracts into a subfolder, not the user's root.
                # Example: 'temp_uploads/sorted/Courses/DSA/file.pdf' -> 'sorted/Courses/DSA/file.pdf'
                relative_path = os.path.relpath(file_path, os.path.dirname(source_dir))

                zipf.write(file_path, relative_path)
    return output_zip_path


# --- Flask Endpoints ---
@app.route("/sort", methods=["POST"])
def sort_directory():
    """
    1. Receives the uploaded ZIP file.
    2. Extracts and sorts the contents using the Sorter class.
    3. Zips the resulting folder.
    4. Returns the ZIP file for download.
    """
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400

    # Check if the file is a ZIP archive
    if not file.filename.lower().endswith(".zip"):
        return "Invalid file type. Please upload a ZIP archive.", 400

    # Secure the file name and define paths
    filename = secure_filename(file.filename)
    uploaded_zip_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # 1. Save the uploaded ZIP
    file.save(uploaded_zip_path)

    # Define the directory where contents will be extracted and sorted
    # We use a unique name derived from the original filename (without extension)
    extracted_dir_name = filename.rsplit(".", 1)[0]
    target_dir = os.path.join(app.config["UPLOAD_FOLDER"], extracted_dir_name)

    # Clean up any existing directory with the same name
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    try:
        # 2. Extract the ZIP contents into the target directory
        with zipfile.ZipFile(uploaded_zip_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)

        sorter_root = target_dir

        # List contents of the target directory
        contents = os.listdir(target_dir)

        # Check if the directory contains exactly one item which is a directory
        if len(contents) == 1:
            potential_sub_dir = os.path.join(target_dir, contents[0])

            if os.path.isdir(potential_sub_dir):
                # If so, the actual files are one level deeper.
                sorter_root = potential_sub_dir
                print(f"Adjusted Sorter root to subfolder: {sorter_root}")

        # 3. Execute the Sorter Logic (The Core Data Structure Phase)
        sorter = Sorter(sorter_root)

        # Build the in-memory Tree
        if not sorter.build_structure_tree():
            return "Error building the sorting structure.", 500

        # Execute the file moves based on the Tree
        sorter.execute_sorting()

        # 4. Package the sorted folder back into a ZIP file
        output_zip_name = f"Sorted_{extracted_dir_name}.zip"
        output_zip_path = os.path.join(app.config["UPLOAD_FOLDER"], output_zip_name)

        package_sorted_directory(sorter_root, output_zip_path)

        # 5. Send the result back to the user
        return send_file(
            output_zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=output_zip_name,
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An internal error occurred during sorting: {str(e)}", 500

    finally:
        # 6. Cleanup (Optional but highly recommended for web services)
        try:
            os.remove(uploaded_zip_path)  # Remove original uploaded zip
            shutil.rmtree(target_dir)  # Remove the extracted and sorted folder
            # Keep the final output_zip_path temporarily until the send_file completes,
            # but ideally, you'd use a signal to clean it up after transmission.
        except Exception as cleanup_e:
            print(f"Cleanup error: {cleanup_e}")


if __name__ == "__main__":
    # Run the application
    # Note: Use a more robust server (like Gunicorn) for production
    app.run(debug=True)
