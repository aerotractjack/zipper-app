import os
import glob
import zipfile
from pathlib import Path
from collections import Counter
import shutil
import tempfile
import sys
from flask import Flask, render_template, request, redirect, session, jsonify
from secret import secret_key

"""
Flask application to automate file zipping process.

This script launches a web application that allows users to specify a directory
path (either in Windows or Unix-style format) via an HTML form. Upon form
submission, the script will convert Windows paths to Unix paths if necessary,
then count the number of unique file bases in the directory (i.e., the filename
excluding the extension).

Files with the same base name that occur exactly four times are selected for
compression. Each group of these files is zipped into a .zip file with a name
matching their common base name, using a temporary directory for zip file
creation to avoid including the zip file in itself.

The resulting .zip files are moved to the original directory, and their names
are stored in a Flask session variable for later access. The number of .zip
files created is also stored in the session data.

The script also prints some logging information to the console, including the
base directory and the number of projects zipped.

Finally, the script redirects the user to a success page, which displays the
names of the .zip files created.

Note: The script assumes that it is being run on a Unix-like system, as it
performs path conversions from Windows to Unix style and uses Unix-style path
separators.
"""

app = Flask(__name__, template_folder="templates")
app.secret_key = secret_key

class DirZipper:

    def __init__(self, base_dir):
        if base_dir[:2] == "Z:":
            print("*")
            base_dir = base_dir.replace(
                r'Z:\Clients', r'/home/aerotract/NAS/main/Clients').replace('\\', '/')
        self.base_dir = Path(base_dir).as_posix()
        print(self.base_dir)

    def collect_filenames(self):
        files = os.listdir(self.base_dir)
        files = set([f.split(".")[0] for f in files])
        return files

    def zip_files(self, filenames):
        zipped = []
        for f in filenames:
            zipped.append(self.zip_from_filename(f))
        return zipped

    def zip_from_filename(self, filename):
        with tempfile.TemporaryDirectory() as tempdir:
            zipfname_temp = f"{tempdir}/{filename}.zip"
            zipf = zipfile.ZipFile(zipfname_temp, 'w', zipfile.ZIP_DEFLATED)
            for file in glob.glob(f"{self.base_dir}/{filename}.*"):
                zipf.write(file)
            zipf.close()
            zipfname_final = f"{self.base_dir}/{filename}.zip"
            shutil.move(zipfname_temp, zipfname_final)
        return zipfname_final

    @classmethod
    def zip_dir(cls, base_dir):
        z = cls(base_dir)
        filenames = z.collect_filenames()
        print(filenames)
        zipped = z.zip_files(filenames)
        return z.base_dir, zipped, len(zipped)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        base_dir = request.form.get('base_dir')
        base_dir, zipped, count = DirZipper.zip_dir(base_dir)
        session["zipped"] = zipped
        session["count"] = count
        sys.stdout.flush()
        print("=================")
        print("Base dir: ", base_dir)
        print("Projects zipped: ", len(zipped))
        print("=================")
        sys.stdout.flush()
        return redirect("/success")
    return render_template("home.html")

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html', filenames=session.get("zipped", []))

if __name__ == "__main__":
    app.run(port=6066, host="0.0.0.0")
