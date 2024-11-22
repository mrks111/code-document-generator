# Code README Generator Documentation

## Overview

  Based on the provided summaries, the project is a software utility designed to assist in the documentation and understanding of a Python-based software project. The tool has several features aimed at making the documentation process easier, faster, and more consistent. 
  It can perform a directory-level analysis of Python projects, identify main scripts, calculate token counts for cost estimation purposes, extract dependencies or requirements from Python files, and generate detailed summaries of both individual files and the whole project. 
  Finally, it also has the capability to structure a comprehensive README file, including project overview, features, installation instructions, usage guide, dependencies, and file descriptions. The generated README is created following a particular template provided in one of the code files, which makes sure the structure is consistent across different projects.
  The overall workflow of the project starts from interfacing with the user for directory selection, then analyzing the files one by one, and finally generating a comprehensive README file. It aims to provide an automated way to analyze and understand Python-based projects quickly.
  
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
