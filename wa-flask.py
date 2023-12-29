from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import datetime
import subprocess
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename) # Sanitize the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S") # Get current timestamp
            filename = f"{timestamp}-{filename}" # Append timestamp to filename
            upload_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static') # Upload directory, pointing to ./static
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            # Extract the base filename without extension
            base_filename = os.path.splitext(filename)[0]

            # Create output directory
            output_dir = os.path.join(upload_dir, base_filename, "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Trigger scripts:
            subprocess.run(["python3", "wa-stats-flask.py", filepath])
            subprocess.run(["python3", "wa-graphs.py", filepath])
            # Optional: trigger n8n workflow here
            return redirect(url_for('output', filename=filename)) # Redirect to output page
    return render_template('upload.html')

@app.route('/static/<filename>') # Output page with filename as parameter (e.g. output/WhatsApp Chat with John.txt)
def output(filename): 
    # Extract the base filename without extension
    base_filename = os.path.splitext(filename)[0]
    # Read the summary.html file and extract the table
    with open(os.path.join('static', base_filename, 'output', 'summary.html'), 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        table_html = str(soup.find('table'))
    # Retrieve and display the output from your workflow
    return render_template('output.html', filename=base_filename, table_html=table_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
