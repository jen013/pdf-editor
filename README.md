# PDF Editor

PDF Editor is an application that lets users do basic PDF edits, such as cropping, scaling, and merging PDF files. Utilizing a simple text-based user interface (TUI), users can adapt their existing PDF files to create new ones.

> [!IMPORTANT]
> Although there have been no instances of this application causing unintended modifications to existing files, **it is still recommended to backup important files** before using with a new application, especially one that reads/writes data such as PDF Editor.

## Features

- Merge PDF files by adding them to the editor.
- Customize which pages to add and remove.
- Make various PDF page modifications such as:
  - Cropping pages
  - Scaling pages
  - Resetting your edits
- Create and name your new PDF file.
- Preview the PDF file before saving.

## Install and Run

Python 3 is required. 

> **Note:** This project was created using Python 3.11.

All dependencies are listed in `requirements.txt` and need to be installed. It is recommended to use a virtual environment, such as  [venv](https://docs.python.org/3/library/venv.html), to run this project. 

#### Download the project from the [GitHub repository](https://github.com/jen013/pdf-editor) or through your shell using [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

```shell
# Install project using git
git clone https://github.com/jen013/pdf-editor.git

# Navigate into project root directory
cd pdf-editor
```

#### **Recommended:** Create and activate a virtual environment.

> **Note:** Specific commands will vary depending on your operating system, shell, and choice of virtual environment.
See [Creating virtual environments](https://docs.python.org/3/library/venv.html#creating-virtual-environments) and [How venvs work](https://docs.python.org/3/library/venv.html#how-venvs-work) for more information and specific commands for venv.

```shell
# Create venv virtual environment on Windows
python -m venv .env

# Activate virtual environment on Windows with cmd.exe
.env\Scripts\activate.bat
```

#### Install dependencies from `requirements.txt`.

```shell
# In 'pdf-editor' directory
pip install -r requirements.txt
```

#### Run PDF Editor.

```shell
# In 'pdf-editor' directory on Windows
python src\pdfeditor
```

## Future Development

- Improve readability and look of TUI.
- Allow users to rearrange their pages in the editor.
- Update packaging and installation directions to be more in line with modern Python standards.