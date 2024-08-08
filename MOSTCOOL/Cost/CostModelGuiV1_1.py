from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objs as go
import plotly.io as pio
from CostModelFileCalculationsV1_1 import variables, dataCenterDetails, Cooling_System_Details_Ref, Cooling_System_Details_Analysis, update_cooling_system_details, get_cooling_system_details, get_redundancy_multiplier, calculate_total_cooling_cost, calculate_irr, format_currency
from CostModelFileProcessingV1_1 import table_lookup, process_html_content, extract_energy_value
import json

app = Flask(__name__, template_folder='CostTemplates')
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

@app.route('/')
def index():
    try:
        if 'cooling_system_details_ref' not in session:
            session['cooling_system_details_ref'] = get_cooling_system_details("reference")
        if 'cooling_system_details_analysis' not in session:
            session['cooling_system_details_analysis'] = get_cooling_system_details("analysis")
        if 'variables' not in session:
            session['variables'] = variables
        if 'data_center_details' not in session:
            session['data_center_details'] = dataCenterDetails
        if 'graphs_displayed' not in session:
            session['graphs_displayed'] = {
                'npvGraph': False,
                'roiGraph': False,
                'irrGraph': False
            }

        cooling_system_details_ref = json.dumps(session['cooling_system_details_ref'])
        cooling_system_details_analysis = json.dumps(session['cooling_system_details_analysis'])
        variables_data = json.dumps(session['variables'])
        data_center_details = json.dumps(session['data_center_details'])
        graphs_displayed = json.dumps(session['graphs_displayed'])

        return render_template(
            'index.html',
            cooling_system_details_ref=cooling_system_details_ref,
            cooling_system_details_analysis=cooling_system_details_analysis,
            variables=variables_data,
            data_center_details=data_center_details,
            graphs_displayed=graphs_displayed
        )
    except Exception as e:
        print(f"Error in index route: {e}")
        return str(e), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Process form submission
        for var in variables:
            variables[var] = request.form.get(var)
        session['variables'] = variables  # Save to session
        return redirect(url_for('index'))
    return render_template('settings.html', variables=variables)

@app.route('/dataCenter', methods=['GET', 'POST'])
def dataCenter():
    if request.method == 'POST':
        # Process form submission
        for var in dataCenterDetails:
            dataCenterDetails[var] = request.form.get(var)
        session['dataCenterDetails'] = dataCenterDetails  # Save to session
        return redirect(url_for('index'))
    return render_template('dataCenter.html', variables=dataCenterDetails)

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

        # Assuming process_html_content returns a DataFrame
        df = process_html_content(file_content)
        updated_lookup = {key: table_lookup[key]['value'] for key in table_lookup}

        # Extract energy value and duration
        energy_per_hour = extract_energy_value(df)

        update_cooling_system_details(mtbf, gamma, beta, eta, cost_per_maintenance_event, Cooling_System_Details_Ref)
        cooling_system_details = get_cooling_system_details(Cooling_System_Details_Ref)
        total_cooling_cost = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Ref))

        # Save to session
        session['table_data'] = cooling_system_details
        session['total_cooling_cost'] = total_cooling_cost
        print(cooling_system_details)
        print(energy_per_hour)

        return jsonify({
            "table_lookup": updated_lookup,
            "cooling_system_details": cooling_system_details,
            "total_cooling_cost": total_cooling_cost,
            "energy_per_hour": energy_per_hour
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/duplicateTable', methods=['POST'])
def duplicate_table():
    try:
        data = request.json
        print("Received data:", data)  # Debugging line
        table_data = data['tableData']
        percentage = float(data['percentage'])
        print("Percentage received:", percentage)  # Debugging line

        # Perform duplication logic based on the percentage
        Cooling_System_Details_Analysis = copy.deepcopy(Cooling_System_Details_Ref)  # Deep copy of the original details

        for row in table_data[1:]:  # Skip the first row
            component_name = row[1]
            # Find the corresponding key in Cooling_System_Details_Analysis
            original_name = None
            for key in Cooling_System_Details_Analysis.keys():
                if Cooling_System_Details_Analysis[key]['Name'] == component_name:
                    original_name = key
                    break

            if original_name:
                original_cost_value = Cooling_System_Details_Analysis[original_name]['Cost_per_equipment']
                
                if isinstance(original_cost_value, str):
                    try:
                        original_cost = float(original_cost_value.replace('$', '').replace(',', ''))
                    except ValueError:
                        print(f"Invalid cost value for {original_name}: {original_cost_value}")
                        original_cost = 0.0
                elif isinstance(original_cost_value, float):
                    original_cost = original_cost_value
                else:
                    print(f"Unexpected cost value type for {original_name}: {type(original_cost_value)}")
                    original_cost = 0.0
                
                print(f"Original cost for {original_name}: {original_cost}")  # Debugging line
                
                new_cost = original_cost * (percentage / 100.0)
                Cooling_System_Details_Analysis[original_name]['Cost_per_equipment'] = new_cost
                Cooling_System_Details_Analysis[original_name]['Total_cost_of_cooling_system'] = new_cost * get_redundancy_multiplier(Cooling_System_Details_Analysis[original_name]['Redundancy'])
                print(f"Updated cost for {original_name}: {new_cost}")  # Debugging line
            else:
                print(f"Component name '{component_name}' not found in Cooling_System_Details_Analysis")  # Debugging line

        cooling_system_details_analysis = get_cooling_system_details(Cooling_System_Details_Analysis)
        print("Updated Cooling System Details:", cooling_system_details_analysis)  # Debugging line

        return jsonify({
            "cooling_system_details_analysis": cooling_system_details_analysis
        })
    except Exception as e:
        print("Error in duplicate_table:", str(e))  # Debugging line
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

        print(f"Received data: {data}")
        print(f"Indices to remove: {indices}")
        print(f"File ID: {file_id}")

        if not indices:
            raise ValueError("No indices provided")

        # Determine which cooling system to update
        if file_id == 'file1':
            cooling_system = Cooling_System_Details_Ref
            print("Updating Cooling_System_Details_Ref")
        else:
            cooling_system = Cooling_System_Details_Analysis
            print("Updating Cooling_System_Details_Analysis")

        component_keys = list(cooling_system.keys())
        print(f"Component keys before removal: {component_keys}")

        # Remove the corresponding rows based on the provided indices
        for index in sorted(indices, reverse=True):
            if index < len(component_keys):
                component_name = component_keys[index]
                print(f"Removing component at index {index}: {component_name}")
                del cooling_system[component_name]
            else:
                print(f"Index {index} is out of range. Skipping.")

        # Retrieve updated cooling system details
        if file_id == 'file1':
            cooling_system_details = get_cooling_system_details('reference')
            total_cooling_cost = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Ref))
        else:
            cooling_system_details = get_cooling_system_details('analysis')
            total_cooling_cost = format_currency(calculate_total_cooling_cost(Cooling_System_Details_Analysis))

        print(f"Updated cooling system details: {cooling_system_details}")
        print(f"Total cooling cost: {total_cooling_cost}")

        return jsonify({
            'cooling_system_details': cooling_system_details,
            'total_cooling_cost': total_cooling_cost
        })
    except Exception as e:
        print(f"Error in remove_cooling_system: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/save', methods=['POST'])
def save():
    session['Cooling_System_Details_Ref'] = Cooling_System_Details_Ref
    session['Cooling_System_Details_Analysis'] = Cooling_System_Details_Analysis
    session['variables'] = variables
    session['dataCenterDetails'] = dataCenterDetails
    session['tables_displayed'] = True
    return jsonify({"message": "State saved successfully"})

@app.route('/load', methods=['POST'])
def load():
    global Cooling_System_Details_Ref, Cooling_System_Details_Analysis, variables, dataCenterDetails

    if 'Cooling_System_Details_Ref' in session:
        Cooling_System_Details_Ref = session['Cooling_System_Details_Ref']
    if 'Cooling_System_Details_Analysis' in session:
        Cooling_System_Details_Analysis = session['Cooling_System_Details_Analysis']
    if 'variables' in session:
        variables = session['variables']
    if 'dataCenterDetails' in session:
        dataCenterDetails = session['dataCenterDetails']

    tables_displayed = session.get('tables_displayed', False)
    return jsonify({
        "message": "State loaded successfully",
        "tables_displayed": tables_displayed,
        "table_data": session.get('table_data', []),
        "table_data_analysis": session.get('table_data_analysis', []),
        "total_cooling_cost": session.get('total_cooling_cost', ''),
        "energy_value": session.get('energy_value', '')
    })

@app.route('/load_state', methods=['POST'])
def load_state():
    try:
        state = request.get_json()
        session['cooling_system_details_ref'] = state.get('coolingSystemDetailsRef')
        session['cooling_system_details_analysis'] = state.get('coolingSystemDetailsAnalysis')
        session['variables'] = state.get('variables')
        session['data_center_details'] = state.get('dataCenterDetails')
        session['graphs_displayed'] = state.get('graphsDisplayed')
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error loading state: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Change port if issues arise
