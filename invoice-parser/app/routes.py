import os
import csv
from flask import current_app as app, render_template, request, send_file
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
from io import StringIO, BytesIO


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the uploaded files
        uploaded_files = request.files.getlist('files')
        
        # Load templates from the specified folder
        template_folder = os.path.join(app.root_path, 'invoice2data/templates')
        templates = read_templates(template_folder)

        # Prepare a list to store extracted data
        extracted_data = []

        for file in uploaded_files:
            # Save the uploaded file temporarily
            file_path = os.path.join(app.root_path, 'temp', file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

            # Extract data using invoice2data
            data = extract_data(file_path, templates=templates)
            if data:
                extracted_data.append(data)

            # Remove the temporary file
            os.remove(file_path)

        # Generate a CSV file from the extracted data
        csv_output = StringIO()
        csv_writer = csv.DictWriter(csv_output, fieldnames=extracted_data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(extracted_data)
        csv_output.seek(0)

        # Convert the StringIO content to BytesIO for binary mode
        binary_csv = BytesIO(csv_output.getvalue().encode('utf-8'))

        # Send the CSV file as a downloadable response
        return send_file(
            binary_csv,
            mimetype='text/csv',
            as_attachment=True,
            download_name='invoices.csv'
        )

    # Render the index.html template for GET requests
    return render_template('index.html')

