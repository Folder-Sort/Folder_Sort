import os
import shutil

# --- Custom Data Structure: DirectoryNode (The Tree) ---
class DirectoryNode:
    """
    Represents a node in the directory structure tree.
    (No changes here, the core data structure is sound)
    """
    def __init__(self, name, is_file=False):
        self.name = name
        self.is_file = is_file
        self.children = {}  # Dictionary mapping child name to DirectoryNode object

    def add_child(self, name, is_file=False):
        """
        The primary method for building the tree. 
        It checks if a child (folder) already exists by name; 
        if so, it returns the existing node; otherwise, it creates and adds a new one.
        """
        if name not in self.children:
            self.children[name] = DirectoryNode(name, is_file)
        return self.children[name]

    def __repr__(self):
        return f"<Node: {self.name}{' (FILE)' if self.is_file else ''} with {len(self.children)} children>"

# --- Sorter Class (The Algorithm) ---
class Sorter:
    """
    Scans a directory, builds a DirectoryNode tree representing the
    sorted structure, and then executes the file operations.
    """
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.structure_tree = DirectoryNode("ROOT") 
        
        # 2. Key Mappings (The 'Rules' for Sorting)
        
        # 🌟 FIX: Updated self.course_map with user's specific entries
        self.course_map = {
            'data structures': 'Data Structures and Algorithms',
            'dsa': 'Data Structures and Algorithms',
            'algorithm': 'Data Structures and Algorithms',
            'image': 'Image Processing',
            'computer vision': 'Image Processing',
            'dip': "Image Processing",
            'ccna': 'CCNA Networking',
            'network': 'CCNA Networking',
            'control': 'Control Engineering',
            'pid': 'Control Engineering',
            'nlp': 'Natural Language Processing (NLP)',
            'machine learning': 'Machine Learning (ML)',
            'ml': 'Machine Learning (ML)',
            'deep learning': 'Machine Learning (ML)',
            'ai': 'Machine Learning (ML)',
            'communication': 'Communication and Presentation Skills',
            'statistics': 'Statistics'
        }
        
        # 🌟 FIX: Separate folders for PDF, DOCX, and PPTX
        self.ext_map = {
            # Videos
            '.mp4': 'Videos', '.avi': 'Videos', '.mov': 'Videos', '.mkv': 'Videos',
            # Documents/Lectures
            '.pdf': 'Lecture Notes (PDF)', 
            '.docx': 'Lecture Notes (DOCX)', 
            '.pptx': 'Presentations (PPTX)',
            # Code Files (Source/Header)
            '.py': 'Code', 
            '.java': 'Code', 
            '.cpp': 'Code', 
            '.c': 'Code', 
            '.js': 'Code',
            '.h': 'Code',        
            '.hpp': 'Code',      
            # Executables
            '.exe': 'Executables', 
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
        # Default for unrecognized extension
        file_type_folder = self.ext_map.get(ext, 'Unclassified') 
        
        # Determine Course Folder
        course_folder = 'Unsorted' # Default course
        
        # Check for keywords in the filename (case-insensitive)
        name_lower = filename.lower()
        
        # NOTE: Since we iterate through the map, the first match wins.
        # Ensure your most specific keywords (like 'dsa') come before general ones 
        # (like 'data') if you were to change the map ordering, but for simple
        # matching, the current iteration is fine.
        for keyword, course_name in self.course_map.items():
            if keyword in name_lower:
                course_folder = course_name
                break # Stop at the first match

        return course_folder, file_type_folder

    def build_structure_tree(self):
        """
        Scans the root directory and builds the DirectoryNode tree structure
        in memory based on the classification rules.
        """
        print("\n--- Phase 1: Building Tree Structure in Memory ---")
        
        # Add the default 'Unsorted' folder to the root
        self.structure_tree.add_child('Unsorted') 
        
        # Iterate through all items in the root directory
        try:
            for item in os.listdir(self.root_dir):
                item_path = os.path.join(self.root_dir, item)
                
                # Only process files
                if os.path.isfile(item_path):
                    
                    course, file_type = self._get_classification(item)
                    
                    # 1. Get/Create the Course Node (e.g., 'Data Structures and Algorithms')
                    # This implicitly creates the node if it doesn't exist.
                    course_node = self.structure_tree.add_child(course)
                    
                    # 2. Get/Create the Type Node (e.g., 'Videos') under the Course Node
                    type_node = course_node.add_child(file_type)
                    
                    # 3. Add the File as a leaf node under the Type Node
                    type_node.add_child(item, is_file=True)
                    
                    print(f"  > Classified '{item}' to: {course}/{file_type}")
                
                # Exclude subdirectories (folders) from processing
                elif os.path.isdir(item_path):
                    print(f"  > Skipping existing directory: {item}")
                    
        except FileNotFoundError:
            print(f"Error: Directory not found at {self.root_dir}")
            return False
            
        print("Tree building complete.")
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
            
            if not course_node.children and course_name != 'Unsorted':
                print(f"  ** Skipping empty course folder: {course_name}")
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
                            print(f"      ! WARNING: Source file not found: {file_name}. Already moved or missing.")
                        except Exception as e:
                            print(f"      ! ERROR moving {file_name}: {e}")
                            
        print("\n--- Sorting Complete! ---")


# # --- Main Execution ---
# if __name__ == "__main__":
    
#     # ! YOU MUST CHANGE THIS TO YOUR ACTUAL DIRECTORY PATH 
#     TARGET_DIRECTORY = "./test_dir" 

#     # 2. Initialize and Run Sorter
#     if os.path.isdir(TARGET_DIRECTORY):
#         sorter = Sorter(TARGET_DIRECTORY)
        
#         if sorter.build_structure_tree():
#             sorter.execute_sorting()
#     else:
#         print(f"Error: Target directory not found or is not a directory: {TARGET_DIRECTORY}")
#         print("Please ensure the path is correct and the folder exists.")