# Code README Generator Documentation

This utility automates documentation for Python projects. Key features include:

  - Directory-level analysis
  - Main script identification
  - Token counting for cost estimation
  - Dependency extraction
  - File and project summarization
  - README generation with consistent structure

The tool streamlines project analysis and documentation, making it easier for developers to understand and share their Python projects on GitHub.
  
## Features

1. **Purpose**:

     The code in the file is designed to analyze a Python project at a directory level, identify main scripts, calculate token counts for cost estimation, extract requirements, leverage OpenAI for automated Python code analysis, generate summaries of individual files and the entire project, and finally structure a comprehensive README file with all gathered information.

2. **Key Features**:
  - A GUI interface for folder selection.
  - Directory scanning and traversal to find main Python files.
  - Extraction of dependencies or requirements from the Python files.
  - Token counting for cost estimation.
  - Use of OpenAI for code analysis and explanation.
  - Generation of a structured README, including project overview, features, installation instructions, usage guide, dependencies, and file descriptions.
  - Ability to identify the main script of the project by searching for `if __name__ == "__main__"` in the files.

3. **Dependencies**: The external libraries used in the file include:
  - `prompts`
  - `dotenv`
  - `tkinter`
  - `tqdm`
  - `tiktoken`
  - `openai`

## Installation

To install the dependencies for the tool, run:
    
    pip install -r requirements.txt

## How to Use

  1. Navigate to the project directory:
     
    git clone <github-download-link>
    cd <project-directory>

  2. Ensure all dependencies are installed

  4. Run the main script:

    python documentor.py
