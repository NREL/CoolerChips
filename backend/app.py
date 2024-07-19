from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app)
@app.route('/')
def home():
    return "Hello World!"

@app.route('/api/send-edge', methods=['POST'])
def check_function():
    edges_data = request.json.get('nodeDetails')
    print(edges_data)
    return jsonify({"message": "Checked"})

@app.route('/api/send-edges', methods=['POST'])
def receive_edges():
    data = request.json
    print(data)
    edges = data.get('edges')
    nodeDetails = data.get('nodeDetails')
    eval_method = data.get('calculationType')
    if not edges:
        return jsonify({"ALERT": "No connection between blocks"})

    edges_df = pd.DataFrame(edges)
    nodeDetails_df = pd.DataFrame(nodeDetails)
    nodeDetails_df = pd.DataFrame.from_dict(nodeDetails, orient='index').reset_index()
    nodeDetails_df.columns = ['id', 'reliability', 'mtbf', 'mttr']

    # Calculate Availability for each node
    nodeDetails_df['availability'] = nodeDetails_df['mtbf'] / (nodeDetails_df['mtbf'] + nodeDetails_df['mttr'])

    # Keep only necessary columns
    nodeDetails_df = nodeDetails_df[['id', 'reliability', 'availability']]

    # Merge the DataFrames on the node id for source
    merged_df = pd.merge(edges_df, nodeDetails_df, how='left', left_on='source', right_on='id')

    nodes = set(edges_df['source']).union(set(edges_df['target']))
    data = []

    for node in nodes:
        connected_to = edges_df[edges_df['source'] == node]['target'].tolist()
        connected_from = edges_df[edges_df['target'] == node]['source'].tolist()
        node_info = nodeDetails_df[nodeDetails_df['id'] == node].iloc[0].to_dict()
        data.append({
            'RBD_Label': node,
            'Connected_To': '-'.join(connected_to) if connected_to else None,
            'Connected_From': '-'.join(connected_from) if connected_from else None,
            'Reliability': node_info['reliability'],
            'Availability': node_info['availability']
        })

    print(data)  # For debugging

    # Create the final DataFrame
    df = pd.DataFrame(data)
    print(df)

    def calculate_parallel(paths):
        result = 1 - np.prod([1 - path for path in paths])
        print(f"  Parallel calculation: 1 - prod(1 - {paths}) = {result}")
        return result

    def calculate_series(paths):
        result = 1
        for path in paths:
            result *= path
        print(f"Series calculation: product{paths} = {result}")
        return result

    def process_junction(df, junction, processed, depth=""):
        print(f"{depth}Processing junction: {junction}")
        if junction in processed:
            print(f"{depth}Junction {junction} already processed, returning its value")
            return df.loc[df['RBD_Label'] == junction, eval_method].values[0]
        
        processed.add(junction)
        connected_to = df.loc[df['RBD_Label'] == junction, 'Connected_To'].values[0]
        current_value = df.loc[df['RBD_Label'] == junction, eval_method].values[0]
        
        if pd.isna(connected_to):
            print(f"{depth}End junction {junction} with value {current_value}")
            return current_value
        
        next_junctions = connected_to.split('-')
        
        if len(next_junctions) == 1:
            next_value = process_junction(df, next_junctions[0], processed, depth + " ")
            value = calculate_series([current_value, next_value])
            print(f"{depth}Series result for {junction}: {value}")
        else:
            parallel_values = [process_junction(df, j, processed, depth + " ") for j in next_junctions]
            parallel_result = calculate_parallel(parallel_values)
            value = calculate_series([current_value, parallel_result])
            print(f"{depth}Parallel result for {junction}: {value}")
        
        return value

    def calculate_network(df):
        global eval_method
        start_junction = df.loc[df['Connected_From'].isna(), 'RBD_Label'].values[0]
        
        print(f"Starting calculation from {start_junction}")
        processed = set()
        result = process_junction(df, start_junction, processed)
        print(f"Final result: {result}")
        return result
    
    final_result=calculate_network(df)

    return jsonify({eval_method: "{}".format(final_result)})

if __name__ == '__main__':
    app.run(debug=True)