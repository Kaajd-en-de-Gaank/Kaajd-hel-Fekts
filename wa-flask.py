# Bezig met flask web pagina voor upload / output, zodat het niet via Google drive hoeft. Maar nog niet helemaal functioneel.

from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Pagina voor upload:
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename) # Sanitize the filename
            upload_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static') # Upload directory, pointing to ./static
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            # Trigger scripts:
            subprocess.run(["python3", "wa-stats.py", filepath])
            subprocess.run(["python3", "wa-graphs.py", filepath])
            # Optional: trigger n8n workflow here
            return redirect(url_for('output', filename=filename)) # Redirect to output page
    return render_template('upload.html')

# pagina voor output als de scripts klaar zijn
@app.route('/static/<filename>') # Output page with filename as parameter (e.g. output/WhatsApp Chat with John.txt)
def output(filename): 
    # Retrieve and display the output:
    return render_template('output.html', filename=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
