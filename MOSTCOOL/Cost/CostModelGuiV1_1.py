from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from CostModelFileCalculationsV1_1 import variables, Cooling_System_Details, update_cooling_system_details, get_cooling_system_details, get_redundancy_multiplier, calculate_total_cooling_cost, calculate_irr, format_currency
from CostModelFileProcessingV1_1 import table_lookup, process_html_content

app = Flask(__name__, template_folder='CostTemplates')
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

@app.route('/')
def index():
    # Restore session data if available
    if 'table_data' in session:
        table_data = session['table_data']
    else:
        table_data = get_cooling_system_details()
    
    if 'roi_image' in session and 'irr_image' in session and 'npv_image' in session:
        roi_image = session['roi_image']
        irr_image = session['irr_image']
        npv_image = session['npv_image']
    else:
        roi_image, irr_image, npv_image = calculate_irr()
    
    return render_template('index.html', table_data=table_data, roi_image=roi_image, irr_image=irr_image, npv_image=npv_image)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Process form submission
        for var in variables:
            variables[var] = request.form.get(var)
        session['variables'] = variables  # Save to session
        return redirect(url_for('index'))
    return render_template('settings.html', variables=variables)

@app.route('/elements.html')
def elements():
    return render_template('elements.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    try:
        file_content = request.form.get('fileContent')
        mtbf = request.form.get('mtbf')
        gamma = request.form.get('gamma')
        beta = request.form.get('beta')
        eta = request.form.get('eta')
        cost_per_maintenance_event = request.form.get('costPerMaintenanceEvent')

        if not file_content or not mtbf or not gamma or not beta or not eta or not cost_per_maintenance_event:
            raise ValueError("Missing required form data")

        updated_lookup = process_html_content(file_content)
        update_cooling_system_details(mtbf, gamma, beta, eta, cost_per_maintenance_event)
        cooling_system_details = get_cooling_system_details()
        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        roi_image, irr_image, npv_image = calculate_irr()

        # Save to session
        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost
        session['roi_image'] = roi_image
        session['irr_image'] = irr_image
        session['npv_image'] = npv_image

        return jsonify({
            "table_lookup": updated_lookup,
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "roi_image": roi_image,
            "irr_image": irr_image,
            "npv_image": npv_image
        })
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
        roi_image, irr_image, npv_image = calculate_irr()

        # Save to session
        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost
        session['roi_image'] = roi_image
        session['irr_image'] = irr_image
        session['npv_image'] = npv_image

        return jsonify({
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "roi_image": roi_image,
            "irr_image": irr_image,
            "npv_image": npv_image
        })
    except Exception as e:
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
            component['Cost_per_equipment'] = new_value
        elif cell_index == 3:
            component['MTBF'] = new_value
        elif cell_index == 4:
            component['Gamma'] = new_value
        elif cell_index == 5:
            component['Beta'] = new_value
        elif cell_index == 6:
            component['Eta'] = new_value
        elif cell_index == 7:
            component['Cost_per_maintenance_event'] = new_value
        elif cell_index == 8:
            component['Total_cost_of_cooling_system'] = new_value

        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        roi_image, irr_image, npv_image = calculate_irr()

        # Save to session
        session['table_data'] = get_cooling_system_details()
        session['total_cooling_cost'] = total_cooling_cost
        session['roi_image'] = roi_image
        session['irr_image'] = irr_image
        session['npv_image'] = npv_image

        return jsonify({
            "cooling_system_details": get_cooling_system_details(),
            "total_cooling_cost": total_cooling_cost,
            "roi_image": roi_image,
            "irr_image": irr_image,
            "npv_image": npv_image
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Change port if issues arise
