from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from CostModelFileCalculationsV1_1 import variables, Cooling_System_Details, update_cooling_system_details, get_cooling_system_details, get_redundancy_multiplier, calculate_total_cooling_cost, format_currency, CostModelCalculations
from CostModelFileProcessingV1_1 import table_lookup, process_html_content, process_sqlite_content
import os
import tempfile

app = Flask(__name__, template_folder='CostTemplates')
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    table_data_file1 = session.get('table_data_file1', {})
    table_data_file2 = session.get('table_data_file2', {})
    total_cost = calculate_total_cooling_cost()
    duration = int(variables["Duration of Simulation (seconds)"]) // (60 * 60 * 24 * 365)

    return render_template('index.html', 
                           table_data_file1=table_data_file1, 
                           table_data_file2=table_data_file2, 
                           total_cost=total_cost, 
                           duration=duration)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        for var in variables:
            variables[var] = request.form.get(var)
        session['variables'] = variables
        return redirect(url_for('index'))
    return render_template('settings.html', variables=variables)

@app.route('/elements.html')
def elements():
    return render_template('elements.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    try:
        file_results = {}
        if 'file1' in request.files:
            file1 = request.files['file1']
            file_content = file1.read()

            mtbf = request.form.get('mtbf')
            gamma = request.form.get('gamma')
            beta = request.form.get('beta')
            eta = request.form.get('eta')
            cost_per_maintenance_event = request.form.get('costPerMaintenanceEvent')

            if not file_content:
                raise ValueError("No file content")

            if file1.filename.endswith('.htm') or file1.filename.endswith('.html'):
                updated_lookup = process_html_content(file_content)
            elif file1.filename.endswith('.sql') or file1.filename.endswith('.sqlite'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                updated_lookup = process_sqlite_content(temp_file_path)
                os.remove(temp_file_path)
            else:
                raise ValueError("Unsupported file type")

            file_results['file1'] = updated_lookup
            session['table_data_file1'] = updated_lookup

        if 'file2' in request.files:
            file2 = request.files['file2']
            file_content = file2.read()

            mtbf = request.form.get('mtbf')
            gamma = request.form.get('gamma')
            beta = request.form.get('beta')
            eta = request.form.get('eta')
            cost_per_maintenance_event = request.form.get('costPerMaintenanceEvent')

            if not file_content:
                raise ValueError("No file content")

            if file2.filename.endswith('.htm') or file2.filename.endswith('.html'):
                updated_lookup = process_html_content(file_content)
            elif file2.filename.endswith('.sql') or file2.filename.endswith('.sqlite'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                updated_lookup = process_sqlite_content(temp_file_path)
                os.remove(temp_file_path)
            else:
                raise ValueError("Unsupported file type")

            file_results['file2'] = updated_lookup
            session['table_data_file2'] = updated_lookup

        return jsonify(file_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/update_redundancy', methods=['POST'])
def update_redundancy():
    try:
        index = int(request.form.get('index'))
        redundancy = request.form.get('redundancy')

        if not redundancy:
            raise ValueError("Missing redundancy value")

        component_keys = list(Cooling_System_Details.keys())
        if index >= len(component_keys):
            raise ValueError("Invalid index")

        component = Cooling_System_Details[component_keys[index]]
        component['Redundancy'] = redundancy
        multiplier = get_redundancy_multiplier(redundancy)
        component['Total_cost_of_cooling_system'] = float(component['Cost_per_equipment']) * multiplier

        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        cooling_system_details = get_cooling_system_details()
        duration = int(variables["Duration of Simulation (seconds)"]) // (60 * 60 * 24 * 365)

        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost

        return jsonify({
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "duration": duration
        })
    except Exception as e:
        print(f"Error updating redundancy: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/update_cell', methods=['POST'])
def update_cell():
    try:
        data = request.json
        row_index = data['rowIndex']
        cell_index = data['cellIndex']
        new_value = data['newValue']

        cooling_system_keys = list(Cooling_System_Details.keys())
        component_key = cooling_system_keys[row_index - 1]
        component = Cooling_System_Details[component_key]

        if cell_index == 1:
            component['Name'] = new_value
        elif cell_index == 2:
            component['Units'] = new_value
        elif cell_index == 3:
            component['Cost_per_equipment'] = new_value
        elif cell_index == 4:
            component['Redundancy'] = new_value
        elif cell_index == 5:
            component['MTBF'] = new_value
        elif cell_index == 6:
            component['Gamma'] = new_value
        elif cell_index == 7:
            component['Beta'] = new_value
        elif cell_index == 8:
            component['Eta'] = new_value
        elif cell_index == 9:
            component['Cost_per_maintenance_event'] = new_value
        elif cell_index == 10:
            component['Total_cost_of_cooling_system'] = new_value

        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        cooling_system_details = get_cooling_system_details()
        duration = int(variables["Duration of Simulation (seconds)"]) // (60 * 60 * 24 * 365)

        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost

        return jsonify({
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "duration": duration
        })
    except Exception as e:
        print(f"Error updating cell: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/update_maintenance_type', methods=['POST'])
def update_maintenance_type():
    try:
        index = int(request.form.get('index'))
        maintenance_type = request.form.get('maintenanceType')

        if not maintenance_type:
            raise ValueError("Missing maintenance type value")

        component_keys = list(Cooling_System_Details.keys())
        if index >= len(component_keys):
            raise ValueError("Invalid index")

        component = Cooling_System_Details[component_keys[index]]
        component['Maintenance_type'] = maintenance_type

        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        cooling_system_details = get_cooling_system_details()
        duration = int(variables["Duration of Simulation (seconds)"]) // (60 * 60 * 24 * 365)

        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost

        return jsonify({
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "duration": duration
        })
    except Exception as e:
        print(f"Error updating maintenance type: {e}")
        return jsonify({"error": str(e)}), 400
    

@app.route('/add_cooling_system', methods=['POST'])
def add_cooling_system():
    try:
        data = request.json
        name = data.get('name')
        units = data.get('units')
        cost_per_equipment = data.get('costPerEquipment')
        redundancy = data.get('redundancy')
        mtbf = data.get('mtbf')
        gamma = data.get('gamma')
        beta = data.get('beta')
        eta = data.get('eta')
        cost_per_maintenance_event = data.get('costPerMaintenanceEvent')
        maintenance_type = data.get('maintenanceType')

        if not (name and units and cost_per_equipment and redundancy and mtbf and gamma and beta and eta and cost_per_maintenance_event and maintenance_type):
            raise ValueError("Missing required fields")

        new_entry = {
            'Name': name,
            'Units': units,
            'Cost_per_equipment': cost_per_equipment,
            'Redundancy': redundancy,
            'MTBF': mtbf,
            'Gamma': gamma,
            'Beta': beta,
            'Eta': eta,
            'Cost_per_maintenance_event': cost_per_maintenance_event,
            'Maintenance_type': maintenance_type,
            'Total_cost_of_cooling_system': float(cost_per_equipment) * get_redundancy_multiplier(redundancy)
        }

        Cooling_System_Details[name] = new_entry
        cooling_system_details = get_cooling_system_details()
        total_cooling_cost = format_currency(calculate_total_cooling_cost())

        return jsonify({
            'cooling_system_details': cooling_system_details,
            'total_cooling_cost': total_cooling_cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/remove_cooling_system', methods=['POST'])
def remove_cooling_system():
    try:
        data = request.json
        indices = data.get('indices')
        fileId = data.get('fileId')

        if not indices:
            raise ValueError("No indices provided")

        component_keys = list(Cooling_System_Details.keys())
        for index in sorted(indices, reverse=True):
            if index < len(component_keys):
                del Cooling_System_Details[component_keys[index]]

        cooling_system_details = get_cooling_system_details()
        total_cooling_cost = format_currency(calculate_total_cooling_cost())

        return jsonify({
            'cooling_system_details': cooling_system_details,
            'total_cooling_cost': total_cooling_cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
