# AutoMatch
A Python program that uses SQLite and Tkinter to search for the user's "ideal" car based on certain parameters. Aimed at automotive enthusiasts.

This program was used as an IB HL CS IA submission, which also doubled as a passion project.

## Install

**IMPORTANT:** Please keep all the files in the same folder, or else the program will not work. Most importantly, ensure that the Python program file and the database share the same directory.

### 1. Prerequisites
Make sure you have Python 3 installed on your system. You can download it from [python.org](https://www.python.org/). When installing Python, ensure you add it to PATH to be able to access it from any directory.

### 2. Navigating to Directory
- Open Terminal/CMD
- Execute this command (replace "path/to/project" with your directory):
    ```sh
    cd path/to/project
    ```
  or right-click on the folder and select "Open in Terminal".

  **TIP:** The `ls` command can show you the contents of your current directory.

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```
or
```sh
pip3 install -r requirements.txt
```

If pip is not installed:

- **Windows:**
    ```sh
    python -m ensurepip --default-pip
    ```
- **macOS:**
    ```sh
    sudo easy_install pip
    ```
  or
    ```sh
    sudo install -d pip
    ```
- **Debian/Ubuntu:**
    ```sh
    sudo apt-get install python3-pip
    ```

### 4. Running the Python 3 File
- **Windows:**
    ```sh
    python CS_IA_Car_Sorting_Program.py
    ```
- **macOS/Debian Linux:**
    ```sh
    python3 CS_IA_Car_Sorting_Program.py
    ```

If the program returns an error code such as `No module named "example"`:
```sh
pip install example
```
or
```sh
pip3 install example
```
(replace `example` with the given module name in the error code)

## Google Image API

The program utilizes the Google Custom Search API to enhance its functionality with image search capabilities.

### Usage Notes:
- The API provides generous daily limits suitable for individual use.
- The program can function without this API but benefits from enhanced features when integrated.

For more details on setting up and using the Google Custom Search API, visit [Google Custom Search API Overview](https://developers.google.com/custom-search/v1/overview).

