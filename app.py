import os
import glob
import zipfile
from pathlib import Path
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

The script also logs some logging information to the console, including the
base directory and the number of projects zipped.

Finally, the script redirects the user to a success page, which displays the
names of the .zip files created.

Note: The script assumes that it is being run on a Unix-like system, as it
performs path conversions from Windows to Unix style and uses Unix-style path
separators.
"""

app = Flask(__name__, template_folder="templates")
app.secret_key = secret_key

import os
import glob
from pathlib import Path
import zipfile

from aerologger import AeroLogger
zip_logger = AeroLogger(
    'ZIP Service',
    'ZIPServ/ZIPServ.log'
)

from requires_nas import requires_nas_loop
requires_nas_loop(info_logger=zip_logger.info, error_logger=zip_logger.error)

def log(*msg):
    print(*msg)
    sys.stdout.flush()

class DirZipper:

    def __init__(self, base_dir):
        if base_dir[:2] == "Z:":
            base_dir = base_dir.replace(
                r'Z:\Clients', r'/home/aerotract/NAS/main/Clients').replace('\\', '/')
        self.base_dir = Path(base_dir).as_posix()

    def collect_filenames(self):
        names = set()
        for f in os.listdir(self.base_dir):
            f = Path(f)
            names.add(f.stem)
        return list(names)

    def glob_filenames(self, name):
        globstr = f"{self.base_dir}/{name}.*"
        res = list(glob.glob(globstr))
        return res

    def create_zipfile_from_name(self, name):
        p = (Path(self.base_dir) / name).with_suffix(".zip")
        return p.as_posix()

    def zip_files(self, zipname, filenames):
        with zipfile.ZipFile(zipname, 'w') as zipf:
            for file in filenames:
                zipf.write(file, Path(file).name)

    @classmethod
    def ZipDir(cls, base_dir):
        self = cls(base_dir)
        zipped = []
        for name in self.collect_filenames():
            file_list = self.glob_filenames(name)
            zipname = self.create_zipfile_from_name(name)
            zipped.append(zipname)
            zip_logger.info(json.dumps(
                {
                    "source": file_list,
                    "dest": zipname
                }, indent=4
            ))
            self.zip_files(zipname, file_list)
        return base_dir, zipped, len(zipped)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        base_dir = request.form.get('base_dir')
        base_dir, zipped, count = DirZipper.ZipDir(base_dir)
        session["zipped"] = zipped
        session["count"] = count
        zip_logger.info(f"Completed {len(zipped)} projects")
        return redirect("/success")
    return render_template("home.html")

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html', filenames=session.get("zipped", []))

if __name__ == "__main__":
    app.run(port=6066, host="0.0.0.0")