# prompts.py

# Prompt for file analysis
ANALYZE_CODE_PROMPT = """
You are tasked with analyzing a Python project file to extract concise and actionable information. 
For the given file, generate the following output:

1. **Purpose**: Provide a single sentence summarizing the purpose of the code in the file.
2. **Key Features**: List the main functionalities implemented, described concisely in bullet points.
3. **Dependencies**: Identify external libraries or frameworks used in this file. Ignore standard Python libraries.

File content:
{code_content}
"""

# Prompt for project explanation
EXPLAIN_PROJECT_PROMPT = """
Based on the following file summaries, explain the entire project. Include:
- A clear explanation of the project's purpose.
- How the different files interact with each other.
- The overall structure and flow of the project.

{combined_summary}
"""

# Prompt for README.md structuring
README_TEMPLATE = """
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
