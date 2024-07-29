# CostModelGuiV1_1.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from CostModelFileCalculationsV1_1 import variables, Cooling_System_Details, update_cooling_system_details, get_cooling_system_details
from CostModelFileProcessingV1_1 import table_lookup, process_html_content

app = Flask(__name__, template_folder='CostTemplates')

@app.route('/')
def index():
    return render_template('index.html', Cooling_System_Details=Cooling_System_Details, table_lookup=table_lookup)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Process form submission
        for var in variables:
            variables[var] = request.form.get(var)
        return redirect(url_for('index'))
    return render_template('settings.html', variables=variables)

@app.route('/process_file', methods=['POST'])
def process_file():
    file_content = request.form['fileContent']
    updated_lookup = process_html_content(file_content)
    update_cooling_system_details()
    cooling_system_details = get_cooling_system_details()
    return jsonify({
        "table_lookup": updated_lookup,
        "cooling_system_details": cooling_system_details
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Change port when issues arise

