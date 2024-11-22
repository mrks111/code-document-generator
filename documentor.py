from prompts import ANALYZE_CODE_PROMPT, EXPLAIN_PROJECT_PROMPT, README_TEMPLATE
from dotenv import load_dotenv
from tkinter import filedialog
from tqdm import tqdm
import tkinter as tk
import tiktoken
import hashlib
import pkgutil
import openai
import json
import sys
import re
import os

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: Set default model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Token pricing (adjust based on the OpenAI model you're using)
TOKEN_PRICE = 0.03  # Cost per 1,000 tokens (gpt-4)


VECTOR_STORE_PATH = "vector_store.json"

# Load or initialize vector store
def load_vector_store():
    if os.path.exists(VECTOR_STORE_PATH):
        with open(VECTOR_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_vector_store(store):
    with open(VECTOR_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=4)

# Hash file content for change detection
def hash_file_content(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# Helper function: Calculate tokens
def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Helper Function for Relative Paths
def relative_path(path, base=None):
    """
    Get the relative path from a base directory (default: current working directory).
    """
    if base is None:
        base = os.getcwd()
    return os.path.relpath(path, start=base)

# Step 1: GUI for Folder Selection
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Input Folder")
    return folder_path

# Step 2: Directory Traversal
def get_main_python_files(folder_path):
    main_files = []
    for root, _, files in os.walk(folder_path):
        if "site-packages" in root or "__pycache__" in root:  # Exclude library/dependencies/cached files
            continue
        for file in files:
            if file.endswith(".py") and not (file.endswith(".pyc") or file.endswith(".pyo")):
                main_files.append(os.path.join(root, file))
    return main_files

# Step 3: Estimate costs
def estimate_cost(files):
    total_tokens = 0
    file_data = []
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            tokens = count_tokens(content, model=OPENAI_MODEL)
            total_tokens += tokens
            file_data.append({"path": file_path, "tokens": tokens})
    cost = (total_tokens / 1000) * TOKEN_PRICE
    return cost, total_tokens, file_data


# Step 4: Parse requirements from Python files
def extract_requirements(files):
    """
    Extract external dependencies from Python files.
    It identifies `import` and `from ... import ...` statements,
    skipping standard libraries and including only external libraries.
    """
    # Get a set of standard library modules
    stdlib_modules = set(sys.builtin_module_names)  # Built-in modules
    stdlib_modules.update({module.name for module in pkgutil.iter_modules() if module.ispkg})

    requirements = set()

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Match "import X" or "from X import Y"
            imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
            for module in imports:
                if module not in stdlib_modules:
                    requirements.add(module)

    return sorted(requirements)

# Step 5: AI Analysis Agent
def analyze_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        code_content = file.read()
    
    prompt = f"""
    You are tasked with analyzing a Python project file to extract concise and actionable information. 
    For the given file, generate the following output:
    
    1. **Purpose**: Provide a single sentence summarizing the purpose of the code in the file.
    2. **Key Features**: List the main functionalities implemented, described concisely in bullet points.
    3. **Dependencies**: Identify external libraries or frameworks used in this file. Ignore standard Python libraries.

    File content:
    {code_content}
    """
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional Python developer with expertise in code analysis and documentation."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] Error analyzing {relative_path(file_path)}: {e}")
        return None

# Step 6: AI Project Explanation Agent
def explain_project(files_data):
    combined_summary = "\n\n".join([data["summary"] for data in files_data if data["summary"]])
    prompt = f"""
    Based on the following file summaries, explain the entire project. Include:
    - A clear explanation of the project's purpose.
    - How the different files interact with each other.
    - The overall structure and flow of the project.
    {combined_summary}
    """
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert software developer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] Error in project explanation: {e}")
        return None

# Step 7: Final AI Agent for README Structuring
def structure_readme(project_summary, features, requirements, main_script_name):
    """
    Generate a well-structured and clean README.md file for the project.
    """
    # Template for README
    readme_template = """
    # Project Documentation

    ## Overview

    {project_summary}

    ## Features

    {features}

    ## Installation

    To install the dependencies for this project, run:

    ```bash
    pip install -r requirements.txt
    ```

    ## How to Use

    1. Navigate to the project directory:

    ```bash
    git clone <github-download-link>
    cd <project-directory>
    ```

    2. Ensure all dependencies are installed.

    3. Run the main script:

    ```bash
    python {main_script_name}
    ```

    ## Dependencies

    The project uses the following dependencies (found in `requirements.txt`):
    {requirements}

    ## File Descriptions

    Below is a brief description of the key Python files in this project:

    {file_descriptions}
    """

    # Generate file descriptions from features
    file_descriptions = []
    for feature in features.split("\n"):
        if feature.strip():  # Exclude empty lines
            file_descriptions.append(f"- {feature.strip()}")

    # Format README content
    readme_content = readme_template.format(
        project_summary=project_summary.strip(),
        features="\n".join(f"- {line.strip()}" for line in features.split("\n") if line.strip()),
        requirements="\n".join(f"- {req}" for req in requirements),
        file_descriptions="\n".join(file_descriptions),
        main_script_name=main_script_name
    )

    # Remove excessive blank lines
    readme_content = re.sub(r"\n\s*\n", "\n\n", readme_content).strip()

    return readme_content

# Step 7a: Cleaning README.md before output
def clean_readme(readme_content):
    """
    Cleans up the README.md content by:
    - Removing excess whitespace and tabs.
    - Adding a newline before headings (##, ###).
    - Removing duplicate or redundant sections.
    - Removing references like "this script" or "this project".
    - Normalizing Markdown headers and structure.
    """
    # Remove leading/trailing whitespaces
    readme_content = readme_content.strip()

    # Add a newline before headings (##, ###) if not already present
    readme_content = re.sub(r"(?<!\n)(##+ )", r"\n\1", readme_content)

    # Remove duplicate content (case-insensitive, multiline duplicate blocks)
    lines_seen = set()
    cleaned_lines = []
    for line in readme_content.splitlines():
        # Filter out duplicate lines
        if line.strip().lower() not in lines_seen:
            cleaned_lines.append(line)
            lines_seen.add(line.strip().lower())
    readme_content = "\n".join(cleaned_lines)

    # Remove redundant references like "this script" or "this project"
    readme_content = re.sub(r"\b(this project|this script)\b", "the tool", readme_content, flags=re.IGNORECASE)

    # Normalize code block indentation
    readme_content = re.sub(r"```bash\n\s+", "```bash\n", readme_content)

    # Remove excessive blank lines (more than 1 newline)
    readme_content = re.sub(r"\n\s*\n", "\n\n", readme_content)

    return readme_content

# Step 8: Write README and requirements.txt
def save_output(readme_content, requirements, output_dir):
    # Save README only if valid
    readme_content = clean_readme(readme_content)
    if readme_content:
        readme_path = os.path.join(output_dir, "README.md")
        print(f"[INFO] Saving README.md to {relative_path(readme_path)}...")
        with open(readme_path, "w", encoding="utf-8") as readme_file:
            readme_file.write(readme_content)
    else:
        print("[ERROR] README.md content is empty. Skipping README save.")

# Step 9: Identify Main Script
def identify_main_script(files):
    """
    Identify the main script by searching for `if __name__ == "__main__"` in the files.
    """
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if "__main__" in content:
                print(f"[INFO] Main script identified: {relative_path(file_path)}")
                return os.path.basename(file_path)
    print("[WARN] Main script not found. Defaulting to 'main.py'.")
    return "main.py"

# Main Workflow
def main():
    # Folder Selection
    print("[INFO] Select the project folder for analysis.")
    folder_path = select_folder()
    if not folder_path:
        print("[ERROR] No folder selected. Exiting.")
        return

    # Scan for Python files before creating output directory
    print(f"[INFO] Scanning for Python files in: {relative_path(folder_path)}")
    python_files = get_main_python_files(folder_path)
    if not python_files:
        print("[ERROR] No Python files found! Exiting without creating output directory.")
        return

    print(f"[INFO] Found {len(python_files)} main Python file(s).")
    for file in python_files:
        print(f"       - {relative_path(file, folder_path)}")

    # Prepare Output Directory (only if .py files exist)
    project_name = os.path.basename(folder_path.rstrip("/\\"))
    output_dir = os.path.join(os.getcwd(), "output", project_name)
    os.makedirs(output_dir, exist_ok=True)

    vector_store_path = os.path.join(output_dir, "vector_store.json")

    # Load vector store for the project
    print(f"[INFO] Loading vector store from: {relative_path(vector_store_path)}")
    if os.path.exists(vector_store_path):
        with open(vector_store_path, "r", encoding="utf-8") as f:
            vector_store = json.load(f)
    else:

        # Load or Initialize Vector Store
        vector_store = load_vector_store() if os.path.exists(vector_store_path) else {}

    print(f"[INFO] Scanning for Python files in: {relative_path(folder_path)}")
    python_files = get_main_python_files(folder_path)
    if not python_files:
        print("[ERROR] No Python files found!")
        return

    print(f"[INFO] Found {len(python_files)} main Python file(s).")
    for file in python_files:
        print(f"       - {relative_path(file, folder_path)}")

    # Main Script Identification
    print("[INFO] Identifying main script...")
    main_script_name = identify_main_script(python_files)

    # Extract Requirements
    print("[INFO] Extracting dependencies...")
    requirements = extract_requirements(python_files)
    print(f"[INFO] Dependencies identified: {', '.join(requirements) if requirements else 'None'}")

    # Save Requirements
    requirements_path = os.path.join(output_dir, "requirements.txt")
    print(f"[INFO] Saving requirements.txt to: {relative_path(requirements_path)}")
    with open(requirements_path, "w", encoding="utf-8") as req_file:
        req_file.write("\n".join(requirements))

    # Estimate Costs
    print("[INFO] Calculating token counts and estimated costs...")
    estimated_cost, total_tokens, file_data = estimate_cost(python_files)
    print(f"       - Total tokens: {total_tokens}")
    print(f"       - Estimated cost: ${estimated_cost:.2f}")

    print("[INFO] File-specific token details:")

    # Update or append vector store with new file states
    print("[INFO] Updating vector store with current file states...")
    for file_info in file_data:
        file_path = file_info["path"]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        file_hash = hash_file_content(content)

        # If the file is new or has changed, update or add it
        if file_path not in vector_store or vector_store[file_path]["hash"] != file_hash:
            print(f"[INFO] Updating entry for: {relative_path(file_path)}")
            vector_store[file_path] = {
                "file_path": file_path,
                "hash": file_hash,
                "tokens": file_info["tokens"],
                "summary": None,  # Summary will be added after analysis
            }
        else:
            print(f"  No changes detected for: {file_path}")

    # Save vector store before analysis
    print(f"[INFO] Saving vector store to: {relative_path(vector_store_path)}")
    save_vector_store(vector_store)
    with open(vector_store_path, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, indent=4)

    # Show file-specific token details for debugging
    for file_info in file_data:
        print(f"  File: {file_info['path']}, Tokens: {file_info['tokens']}")

    # User confirmation
    print("\n[INFO] Requirements and vector store have been saved.")
    proceed = input("[PROMPT] Proceed with README.md generation and analysis? (y/N): ").strip().lower()
    if proceed not in ["", "y", "yes"]:
        print("[INFO] Exiting analysis.")
        return

    # Analyze files and generate summaries
    print("[INFO] Starting file analysis...")
    files_data = []
    for file_path, metadata in tqdm(vector_store.items(), desc="[INFO] Analyzing files", unit="file"):
        try:
            if metadata["summary"] is not None:
                tqdm.write(f"[INFO] Skipping unchanged file: {relative_path(file_path)}")
                files_data.append(metadata)
            else:
                tqdm.write(f"[INFO] Analyzing: {relative_path(file_path)}")
                analysis = analyze_code(file_path)
                if analysis:
                    tqdm.write(f"[INFO] Analysis complete for: {relative_path(file_path)}")
                    metadata["summary"] = analysis
                    files_data.append(metadata)

                    # Save updated vector store after each analysis
                    with open(vector_store_path, "w", encoding="utf-8") as f:
                        json.dump(vector_store, f, indent=4)
                else:
                    tqdm.write(f"[ERROR] Skipping file due to analysis failure: {relative_path(file_path)}")
        except Exception as e:
            tqdm.write(f"[ERROR] Analysis failed for: {relative_path(file_path)}")

    print("[INFO] File analysis complete. Compiling project summary...")

    # Compile the final project explanation
    try:
        project_summary = explain_project(files_data)
        if not project_summary:
            print("Project explanation could not be generated due to errors.")
            return
    except Exception as e:
        print(f"Error in project explanation: {e}")
        return

    print("[INFO] Generating feature list...")
    features = "\n".join([data["summary"] for data in files_data])

    print("[INFO] Structuring README...")
    readme_content = structure_readme(project_summary, features, requirements, main_script_name)

    # Save outputs if README is generated
    print(f"[INFO] Saving outputs to: {relative_path(output_dir)}")
    save_output(readme_content, requirements, output_dir)
    print("[SUCCESS] README.md and requirements.txt successfully generated.")

    if not readme_content:
        print("[ERROR] README.md generation failed. Please review the logs.")
        return

    print("[SUCCESS] README.md and requirements.txt successfully generated.")
    print(f"[SUCCESS] Vector store saved in: {relative_path(vector_store_path)}")


if __name__ == "__main__":
    main()
