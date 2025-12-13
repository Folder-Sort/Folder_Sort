import os
import shutil
from collections import defaultdict

# --- Custom Data Structure: DirectoryNode (The Tree) ---
class DirectoryNode:
    """
    Represents a node in the directory structure tree.
    Each node corresponds to a folder or a file in the final structure.
    """
    def __init__(self, name, is_file=False):
        self.name = name
        self.is_file = is_file
        self.children = {}  # Dictionary mapping child name to DirectoryNode object

    def add_child(self, name, is_file=False):
        """Adds a child node (folder or file) to the current node."""
        if name not in self.children:
            self.children[name] = DirectoryNode(name, is_file)
        return self.children[name]

    def __repr__(self):
        """Prints a human-readable representation of the node."""
        return f"<Node: {self.name}{' (FILE)' if self.is_file else ''} with {len(self.children)} children>"

# --- Sorter Class (The Algorithm) ---
class Sorter:
    """
    Scans a directory, builds a DirectoryNode tree representing the
    sorted structure, and then executes the file operations.
    """
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        # 1. ROOT of the Tree
        self.structure_tree = DirectoryNode("ROOT") 
        
        # 2. Key Mappings (The 'Rules' for Sorting)
        
        # Course Mapping: Keywords in filename -> Course Folder Name
        self.course_map = {
            'data structures': 'Data Structures and Algorithms',
            'dsa': 'Data Structures and Algorithms',
            'algorithm': 'Data Structures and Algorithms',
            'image': 'Image Processing',
            'computer vision': 'Image Processing',
            'ccna': 'CCNA Networking',
            'network': 'CCNA Networking',
            'control': 'Control Engineering',
            'pid': 'Control Engineering',
            'nlp': 'Natural Language Processing (NLP)',
            'machine learning': 'Machine Learning (ML)',
            'ml': 'Machine Learning (ML)',
            'deep learning': 'Machine Learning (ML)',
            'ai': 'Machine Learning (ML)',
        }
        
        # Extension Mapping: File extension -> Subfolder Type Name
        self.ext_map = {
            # Videos
            '.mp4': 'Videos', '.avi': 'Videos', '.mov': 'Videos', '.mkv': 'Videos',
            # Documents/Lectures
            '.pdf': 'Lecture Notes/PDFs', '.docx': 'Lecture Notes/PDFs', '.pptx': 'Lecture Notes/PDFs',
            # Code
            '.py': 'Code', '.java': 'Code', '.cpp': 'Code', '.c': 'Code', '.js': 'Code',
            # Other (Default)
            '.txt': 'Other', '.zip': 'Other', '.rar': 'Other',
        }
        
        # Set of course names to ensure they exist under the root
        self.known_courses = set(self.course_map.values())
        
        print(f"Initialized sorter for directory: {self.root_dir}")

    def _get_classification(self, filename):
        """Classifies a file into a Course Folder and a Type Folder."""
        
        # Determine File Type/Extension Folder
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        file_type_folder = self.ext_map.get(ext, 'Unclassified')
        
        # Determine Course Folder
        course_folder = 'Unsorted' # Default course
        
        # Check for keywords in the filename (case-insensitive)
        name_lower = filename.lower()
        for keyword, course_name in self.course_map.items():
            if keyword in name_lower:
                course_folder = course_name
                break

        return course_folder, file_type_folder

    def build_structure_tree(self):
        """
        Scans the root directory and builds the DirectoryNode tree structure
        in memory based on the classification rules.
        """
        print("\n--- Phase 1: Building Tree Structure in Memory ---")
        
        # Ensure initial course folders exist in the tree
        for course_name in self.known_courses:
            self.structure_tree.add_child(course_name)
        
        # Add the default folders
        self.structure_tree.add_child('Unsorted')
        
        # Iterate through all items in the root directory
        try:
            for item in os.listdir(self.root_dir):
                item_path = os.path.join(self.root_dir, item)
                
                # We only process files, skipping folders or the script itself
                if os.path.isfile(item_path):
                    
                    course, file_type = self._get_classification(item)
                    
                    # 1. Get the Course Node (e.g., 'Data Structures and Algorithms')
                    course_node = self.structure_tree.add_child(course)
                    
                    # 2. Get the Type Node (e.g., 'Videos') under the Course Node
                    type_node = course_node.add_child(file_type)
                    
                    # 3. Add the File as a leaf node under the Type Node
                    type_node.add_child(item, is_file=True)
                    
                    print(f"  > Classified '{item}' to: {course}/{file_type}")
                
                # Exclude subdirectories to keep the scope clean, unless they are 
                # part of the destination structure itself
                elif os.path.isdir(item_path) and item not in self.known_courses and item not in ['Unsorted']:
                    print(f"  > Skipping existing directory: {item}")
                    
        except FileNotFoundError:
            print(f"Error: Directory not found at {self.root_dir}")
            return False
            
        print("Tree building complete.")
        # print(self.structure_tree.children) # Optional: inspect the root children
        return True
    
    def execute_sorting(self):
        """
        Traverses the in-memory structure tree and performs the
        actual folder creation and file movement.
        """
        print("\n--- Phase 2: Executing File System Operations (Traversing Tree) ---")
        
        if not self.structure_tree.children:
            print("Tree is empty. Nothing to sort.")
            return

        # Start traversal from the root's children (the Course Folders)
        for course_name, course_node in self.structure_tree.children.items():
            
            # Skip course folders that have no files assigned (no type children)
            if not course_node.children:
                continue
                
            # Create the main Course Folder
            course_path = os.path.join(self.root_dir, course_name)
            os.makedirs(course_path, exist_ok=True)
            print(f"  ** Created/Ensured course folder: {course_name}")
            
            # Traverse the Type Folders under the Course
            for type_name, type_node in course_node.children.items():
                
                # Create the Type Subfolder (e.g., 'Videos')
                type_path = os.path.join(course_path, type_name)
                os.makedirs(type_path, exist_ok=True)
                print(f"    - Created/Ensured type folder: {type_name}")

                # Traverse the Files (leaf nodes)
                for file_name, file_node in type_node.children.items():
                    if file_node.is_file:
                        src_path = os.path.join(self.root_dir, file_name)
                        dest_path = os.path.join(type_path, file_name)
                        
                        try:
                            # Move the file from the root to the new subfolder
                            shutil.move(src_path, dest_path)
                            print(f"      > Moved: {file_name}")
                        except FileNotFoundError:
                            print(f"      ! WARNING: Source file not found: {file_name}")
                        except Exception as e:
                            print(f"      ! ERROR moving {file_name}: {e}")
                            
        print("\n--- Sorting Complete! ---")


# --- Main Execution ---
if __name__ == "__main__":
    
    # !!! CHANGE THIS TO YOUR DIRECTORY PATH !!!
    TARGET_DIRECTORY = "./test_dir"
    
    # 1. Setup - Create a temporary directory and dummy files for testing
    if not os.path.exists(TARGET_DIRECTORY):
        os.makedirs(TARGET_DIRECTORY)
        print(f"Created test directory: {TARGET_DIRECTORY}")
        
    dummy_files = [
        "Data Structures DSA-Lecture 1.pdf",
        "Algorithm-QuickSort-Code.py",
        "ML_Deep Learning Intro.mp4",
        "Image Processing Computer Vision Notes.docx",
        "CCNA Networking Subnetting.pdf",
        "Control Engineering - PID Design.avi",
        "NLP-Text-Pre-processing-Example.ipynb",
        "random_document.txt",
        "misc_file.zip",
        "A-File-With-No-Keyword.log",
        "Another-DSA-Video.mkv"
    ]
    
    # Create the dummy files in the target directory
    for f in dummy_files:
        try:
            with open(os.path.join(TARGET_DIRECTORY, f), 'w') as temp_file:
                temp_file.write(f"This is the content of {f}")
        except Exception as e:
            print(f"Could not create dummy file {f}: {e}")

    # 2. Initialize and Run Sorter
    if os.path.exists(TARGET_DIRECTORY):
        sorter = Sorter(TARGET_DIRECTORY)
        
        if sorter.build_structure_tree():
            sorter.execute_sorting()
    else:
        print("Please create the target directory or adjust the TARGET_DIRECTORY path.")