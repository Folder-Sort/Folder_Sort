# Sortify - Python course content sorter

<image src="./assets/screen.png" alt="Design Image" />

> This project takes your unorganized course files and returns a sorted folder using a Tree-based algorithm

## Data Structures Used:

### 1. `DirectoryNode`:

- This is a custom data structure that represents a node in the folder tree
- Params:
  - `self.name: str`: The name of the folder/file
  - `self.children: dict`: A map of the subfolders/subfiles of the node
  - `self.isFile: bool`: A boolean indicating whether or not the node is a file (leaf), or folder (Node)

### 2. The `Sorter` class:

- This is the class behind the core algorithm.
- It builds a custom multi-child tree
- Params:
  - `self.root_dir: str`: The absolute path of the target file to be sorted
  - `self.structure_tree: DirectoryNode`: The custom multi-child tree
  - `self.course_map: dict`: The map of the courses on which the files will be sorted (Modify as needed)
  - `self.ext_map: dict`: The map of possible file extensions (Modify as needed)
  - `self.known_courses: set`: The course Names (extracted from `self.course_map`)

## installation:

1. Clone the repo:

```bash
git clone https://github.com/Folder-Sort/Folder_Sort
```

2. Install dependancies:

- Install Flask:

```bash
pip install flask
```

- Install frontend deps:

```bash
cd ./frontend/
npm install
```

## Run the app:

- In the root directory, run:

```bash
python app.py
```

- In the frontend directory, run:

```bash
npm run dev
```
