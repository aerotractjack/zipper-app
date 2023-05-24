# Flask File Zipping Web Application
This is a Flask web application designed to automate the process of compressing multiple files in a given directory. The application allows users to specify a directory path via an HTML form and automatically zips files with the same base name.

# Features
- Supports both Windows and Unix-style directory paths.
- Finds files with the same base name that occur exactly four times in the specified directory.
- Compresses each group of these files into a .zip file with a name matching their common base name.
- Automatically handles path conversions from Windows to Unix style.
- Provides a success page displaying the names of the .zip files created.

# Installation
Clone this repository to your local machine.
Install the required Python dependencies:
- `pip install flask`

Run the Flask app:
- `python app.py` OR `./run.sh` (if on an aerotract machine)

# Usage
Navigate to the application in your web browser (default address is http://localhost:6066).
Enter your directory path into the form and submit.
The application will zip the required files and display a success page with the names of the .zip files created.

### Note
This application assumes that it is being run on a Unix-like system, as it performs path conversions from Windows to Unix style and uses Unix-style path separators.