from flask import Flask, render_template, request, jsonify, session
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objs as go
import plotly.io as pio
from CostModelFileCalculationsV1_1 import variables, Cooling_System_Details_Ref, Cooling_System_Details_Analysis, update_cooling_system_details, get_cooling_system_details, get_redundancy_multiplier, calculate_total_cooling_cost, calculate_irr, format_currency
from CostModelFileProcessingV1_1 import table_lookup, process_html_content

app = Flask(__name__, template_folder='CostTemplates')
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

@app.route('/')
def index():
    # Restore session data if available
    table_data = session.get('table_data', get_cooling_system_details(Cooling_System_Details_Ref))
    roi_image = session.get('roi_image')
    irr_image = session.get('irr_image')
    npv_image = session.get('npv_image')

    if not roi_image or not irr_image or not npv_image:
        Time, roi_image, irr_image, npv_image = calculate_irr()

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

        if not all([file_content, mtbf, gamma, beta, eta, cost_per_maintenance_event]):
            raise ValueError("Missing required form data")

        updated_lookup = process_html_content(file_content)
        update_cooling_system_details(mtbf, gamma, beta, eta, cost_per_maintenance_event, Cooling_System_Details_Ref)
        cooling_system_details = get_cooling_system_details(Cooling_System_Details_Ref)
        total_cooling_cost = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Ref))

        # Save to session
        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost
        print(cooling_system_details)

        return jsonify({
            "table_lookup": updated_lookup,
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/duplicateTable', methods=['POST'])
def duplicate_table():
    try:
        # Get the data from the request
        data = request.json.get('tableData', [])
        
        # Ensure data is not empty and in the expected format
        if not data or not isinstance(data, list):
            raise ValueError("Invalid data format")

        # Process the data if needed before returning it
        cooling_system_details = data
        print(cooling_system_details)
        
        return jsonify({
            "cooling_system_details": cooling_system_details
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/generateGraphs', methods=['POST'])
def generate_graphs():
    Time, ROI, IRR, Net_NPV = calculate_irr()

    # Create an array of time points from 0 to time_years
    time_years = list(range(0, int(Time) + 1))

    # Create the Plotly graphs
    figs = []

    # ROI Figure
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(x=time_years, y=ROI, mode='lines+markers', name='ROI'))
    fig_roi.update_layout(
        title='ROI vs Time',
        xaxis_title='Time (years)',
        yaxis_title='ROI',
        legend_title='Metrics'
    )
    figs.append(fig_roi)

    # IRR Figure
    fig_irr = go.Figure()
    fig_irr.add_trace(go.Scatter(x=time_years, y=IRR, mode='lines+markers', name='IRR'))
    fig_irr.update_layout(
        title='IRR vs Time',
        xaxis_title='Time (years)',
        yaxis_title='IRR',
        legend_title='Metrics'
    )
    figs.append(fig_irr)

    # Net NPV Figure
    fig_npv = go.Figure()
    fig_npv.add_trace(go.Scatter(x=time_years, y=Net_NPV, mode='lines+markers', name='Net NPV'))
    fig_npv.update_layout(
        title='Net NPV vs Time',
        xaxis_title='Time (years)',
        yaxis_title='Net NPV',
        legend_title='Metrics'
    )
    figs.append(fig_npv)

    # Save the plots to BytesIO objects and encode in base64
    images = []
    for fig in figs:
        img_bytes = io.BytesIO()
        pio.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        images.append(img_base64)

    return jsonify({
        'roi_image': images[0],
        'irr_image': images[1],
        'npv_image': images[2]
    })

@app.route('/update_redundancy', methods=['POST'])
def update_redundancy():
    try:
        index = int(request.form.get('index'))
        redundancy = request.form.get('redundancy')

        if not redundancy:
            raise ValueError("Missing redundancy value")

        component_keys_ref = list(Cooling_System_Details_Ref.keys())
        component_keys_analysis = list(Cooling_System_Details_Analysis.keys())
        
        if index >= len(component_keys_ref):
            raise ValueError("Invalid index")

        component_ref = Cooling_System_Details_Ref[component_keys_ref[index]]
        component_analysis = Cooling_System_Details_Analysis[component_keys_analysis[index]]

        component_ref['Redundancy'] = redundancy
        component_analysis['Redundancy'] = redundancy
        
        multiplier = get_redundancy_multiplier(redundancy)
        
        component_ref['Total_cost_of_cooling_system'] = float(component_ref['Cost_per_equipment']) * multiplier
        component_analysis['Total_cost_of_cooling_system'] = float(component_analysis['Cost_per_equipment']) * multiplier

        total_cooling_cost_ref = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Ref))
        total_cooling_cost_analysis = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Analysis))

        cooling_system_details_ref = get_cooling_system_details(Cooling_System_Details_Ref)
        cooling_system_details_analysis = get_cooling_system_details(Cooling_System_Details_Analysis)
        
        Time, roi_image, irr_image, npv_image = calculate_irr()

        # Save to session
        session['table_data'] = cooling_system_details_ref
        session['total_cooling_cost'] = total_cooling_cost_ref
        session['roi_image'] = roi_image
        session['irr_image'] = irr_image
        session['npv_image'] = npv_image

        return jsonify({
            "cooling_system_details_ref": cooling_system_details_ref,
            "total_cooling_cost_ref": total_cooling_cost_ref,
            "cooling_system_details_analysis": cooling_system_details_analysis,
            "total_cooling_cost_analysis": total_cooling_cost_analysis,
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
        table_type = data['tableType']  # Determine if it's 'reference' or 'analysis'

        cooling_system_keys = list(Cooling_System_Details_Ref.keys()) if table_type == 'reference' else list(Cooling_System_Details_Analysis.keys())
        component_key = cooling_system_keys[row_index]
        component = Cooling_System_Details_Ref[component_key] if table_type == 'reference' else Cooling_System_Details_Analysis[component_key]

        if cell_index == 1:
            component['Name'] = new_value
        elif cell_index == 2:
            component['Units'] = new_value
        elif cell_index == 3:
            component['Cost_per_equipment'] = new_value
        elif cell_index == 4:
            component['Redundancy'] = new_value
        elif cell_index == 5:
            component['Total_cost_of_cooling_system'] = new_value
        elif cell_index == 6:
            component['MTBF'] = new_value
        elif cell_index == 7:
            component['Gamma'] = new_value
        elif cell_index == 8:
            component['Beta'] = new_value
        elif cell_index == 9:
            component['Eta'] = new_value
        elif cell_index == 10:
            component['Cost_per_maintenance_event'] = new_value
        elif cell_index == 11:
            component['Maintenance_type'] = new_value

        total_cooling_cost = format_currency(calculate_total_cooling_cost())
        Time, roi_image, irr_image, npv_image = calculate_irr()

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


@app.route('/update_maintenance_type', methods=['POST'])
def update_maintenance_type():
    try:
        index = int(request.form.get('index'))
        maintenance_type = request.form.get('maintenanceType')

        if not maintenance_type:
            raise ValueError("Missing maintenance type value")

        component_keys_ref = list(Cooling_System_Details_Ref.keys())
        component_keys_analysis = list(Cooling_System_Details_Analysis.keys())
        
        if index >= len(component_keys_ref):
            raise ValueError("Invalid index")

        component_ref = Cooling_System_Details_Ref[component_keys_ref[index]]
        component_analysis = Cooling_System_Details_Analysis[component_keys_analysis[index]]

        component_ref['Maintenance_type'] = maintenance_type
        component_analysis['Maintenance_type'] = maintenance_type

        total_cooling_cost_ref = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Ref))
        total_cooling_cost_analysis = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Analysis))
        
        cooling_system_details_ref = get_cooling_system_details(Cooling_System_Details_Ref)
        cooling_system_details_analysis = get_cooling_system_details(Cooling_System_Details_Analysis)
        
        session['table_data'] = cooling_system_details_ref
        session['total_cooling_cost'] = total_cooling_cost_ref

        return jsonify({
            "cooling_system_details_ref": cooling_system_details_ref,
            "total_cooling_cost_ref": total_cooling_cost_ref,
            "cooling_system_details_analysis": cooling_system_details_analysis,
            "total_cooling_cost_analysis": total_cooling_cost_analysis,
            "duration": int(variables["Duration of Simulation (years)"]) * (60 * 60 * 24 * 365)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/add_cooling_system', methods=['POST'])
def add_cooling_system():
    try:
        data = request.json
        name = data.get('name')
        cost_per_equipment = data.get('costPerEquipment')
        redundancy = data.get('redundancy')
        mtbf = data.get('mtbf')
        gamma = data.get('gamma')
        beta = data.get('beta')
        eta = data.get('eta')
        cost_per_maintenance_event = data.get('costPerMaintenanceEvent')
        file_id = data.get('fileId')

        if not all([name, cost_per_equipment, redundancy, mtbf, gamma, beta, eta, cost_per_maintenance_event]):
            raise ValueError("Missing required fields")

        new_entry = {
            'Name': name,
            'Units': 'per_datacenter',  # Default value
            'Cost_per_equipment': cost_per_equipment,
            'Redundancy': redundancy,
            'MTBF': mtbf,
            'Gamma': gamma,
            'Beta': beta,
            'Eta': eta,
            'Cost_per_maintenance_event': cost_per_maintenance_event,
            'Total_cost_of_cooling_system': float(cost_per_equipment) * get_redundancy_multiplier(redundancy)
        }

        if file_id == 'file1':
            Cooling_System_Details_Ref[name] = new_entry
            cooling_system_details = get_cooling_system_details(Cooling_System_Details_Ref)
        else:
            Cooling_System_Details_Analysis[name] = new_entry
            cooling_system_details = get_cooling_system_details(Cooling_System_Details_Analysis)

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
        file_id = data.get('fileId')

        if not indices:
            raise ValueError("No indices provided")

        if file_id == 'file1':
            component_keys = list(Cooling_System_Details_Ref.keys())
            for index in sorted(indices, reverse=True):
                if index < len(component_keys):
                    del Cooling_System_Details_Ref[component_keys[index]]
        elif file_id == 'file2':
            component_keys = list(Cooling_System_Details_Analysis.keys())
            for index in sorted(indices, reverse=True):
                if index < len(component_keys):
                    del Cooling_System_Details_Analysis[component_keys[index]]

        if file_id == 'file1':
            cooling_system_details = get_cooling_system_details(Cooling_System_Details_Ref)
        else:
            cooling_system_details = get_cooling_system_details(Cooling_System_Details_Analysis)

        total_cooling_cost = format_currency(calculate_total_cooling_cost())

        return jsonify({
            'cooling_system_details': cooling_system_details,
            'total_cooling_cost': total_cooling_cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Change port if issues arise
