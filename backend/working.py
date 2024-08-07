from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import math
import io
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
    print("edges_df",edges_df)
    if(nodeDetails_df.empty):
        pass
    else:
        nodeDetails_df.columns = ['id', 'reliability', 'mtbf', 'mttr']
        
        # Calculate Availability for each node
        nodeDetails_df['availability'] = nodeDetails_df['mtbf'] / (nodeDetails_df['mtbf'] + nodeDetails_df['mttr'])

        # Keep only necessary columns
        nodeDetails_df = nodeDetails_df[['id', 'reliability', 'availability']]

    # Merge the DataFrames on the node id for source
    # merged_df = pd.merge(edges_df, nodeDetails_df, how='left', left_on='source', right_on='id')

    nodes = set(edges_df['source']).union(set(edges_df['target']))
    data = []
    # print("nodeDetals_df",nodeDetails_df)
    for node in nodes:
        connected_to = edges_df[edges_df['source'] == node]['target'].tolist()
        connected_from = edges_df[edges_df['target'] == node]['source'].tolist()
        if nodeDetails_df.empty:
            node_info = {'reliability': 1, 'availability': 1}
        else:
            node_info = nodeDetails_df[nodeDetails_df['id'] == node].iloc[0].to_dict()
        data.append({
            'RBD_Label': node,
            'Connected_To': '-'.join(connected_to) if connected_to else None,
            'Connected_From': '-'.join(connected_from) if connected_from else None,
            'Reliability': node_info['reliability'],
            'Availability': node_info['availability']
        })

    df = pd.DataFrame(data)
    print(df)
    def break_cycles(df):
        if df['Connected_To'].isna().any() and df['Connected_From'].isna().any():
            return df
        elif(len(df[df['Connected_To'].str.contains('-')])>0):
            # Identify the nodes with parallel connections
            parallel_nodes = df[df['Connected_To'].str.contains('-')]['RBD_Label'].tolist()
            # Set the 'Connected_To' of parallel connections to None
            # df.loc[df['RBD_Label'].isin(parallel_nodes), 'Connected_To'] = None
            for node in parallel_nodes:
                print("Nodes",node)
                # connected_from_nodes = df[df['Connected_To'] == node]['RBD_Label'].tolist()
                # df.loc[df['RBD_Label'].isin(connected_from_nodes), 'Connected_From'] = None
                connected_from_nodes = df[df['Connected_From'] == node]['RBD_Label'].tolist()
                making_none = df.loc[df['RBD_Label'].isin(connected_from_nodes), 'Connected_To']
                print(making_none)
                df.loc[df['RBD_Label'].isin(connected_from_nodes), 'Connected_To'] = None
                df.loc[df['RBD_Label'].isin(making_none), 'Connected_From'] = None
                parallel_nodes=[]
                return df
        else:
            node_name=df.iloc[0]['RBD_Label']
            print(node_name)
            connected_from_node_name =df.loc[df['RBD_Label'] == node_name, 'Connected_To']
            print(connected_from_node_name)
            df.loc[df['RBD_Label'] == node_name, 'Connected_To'] = None
            df.loc[df['RBD_Label'] == connected_from_node_name[0], 'Connected_From'] = None

            return df
        # Create the final DataFrame
    df = break_cycles(df)
    print(df)

    def calculate_parallel(paths):
        result = 1 - np.prod([1 - round(path,20) for path in paths])
        print(f"Parallel calculation: 1 - prod(1 - {paths}) = {result}")
        return result

    def calculate_series(paths, df, junction):
        
        connected_from = df.loc[df['RBD_Label'] == junction, 'Connected_From'].values[0]
        connected_to = df.loc[df['RBD_Label'] == junction, 'Connected_To'].values[0]
        # print("Junction", junction)
        # print("Connected_from", connected_from)
        # print("Connected_to", connected_to)

        if connected_to is not np.nan:
            if '-' not in connected_to:
                connected_to_nex = df.loc[df['RBD_Label'] == connected_to, 'Connected_From'].values[0]
            else:
                connected_to_split = connected_to.split('-')
                connected_to_nex = df.loc[df['RBD_Label'] == connected_to_split[0], 'Connected_From'].values[0]
            # print("Connected_to_nex", connected_to_nex)

        
        # if connected_from is np.nan:
        #     print("Paths", paths)
        #     for path in paths:
        #         result *= path
        #     print(f"Series calculation: product{paths} = {result}")
        #     return result
        if '-' in connected_to_nex:
            # return 1
            return df.loc[df['RBD_Label'] == junction, eval_method].values[0]
        elif '-' not in connected_to_nex:
            result=1
            print("Result", result)
            for path in paths:
                result = round(result,15) * round(path,15)
            print(f"Series calculation: product{paths} = {result}")
            return result

    def process_junction(df, junction, processed, depth=""):
        global series_junction_value,series_junction_list,series_junction
        series_junction_value=1
        series_junction=None
        series_junction_list=[]
        print(f"{depth}Processing junction: {junction}")
        if junction in processed:
            series_junction=df.loc[df['RBD_Label'] == junction, "Connected_From"].values[0]
            series_junction_list=series_junction.split('-')
            print(f"{depth}Junction {junction} already processed, returning its components list{series_junction_list}")
            series_junction_value = df.loc[df['RBD_Label'] == junction, eval_method].values[0]
            print(f"{depth}Junction {junction} already processed, returning its value {series_junction_value}")
            print(f"{depth}Processed Junctions: {processed}")
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
            value = calculate_series([current_value, next_value,1], df, junction)
            print(f"{depth}Series result for {junction}: {value}")
            df.loc[df['RBD_Label'] == junction, eval_method] = value
        else:
            parallel_values = [process_junction(df, j, processed, depth + " ") for j in next_junctions]
            parallel_result = calculate_parallel(parallel_values)
            if not (set(series_junction_list).issubset(processed)):
                series_junction_value=1
            print("Series junction value check in parallel",series_junction_list,series_junction_value)
            value = calculate_series([current_value, parallel_result, series_junction_value], df, junction)
            df.loc[df['RBD_Label'] == junction, eval_method] = value
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

@app.route('/api/valvemtbfdata', methods=['POST'])
def valve_mtbf_data():
    valve_data=request.json
    print("Received valve data:", valve_data)
    def valve(Nc,dP,Qf,mu,B,DS,nu,Fr_actual,Fr_rated):
        #number of cycles per hour 
        # Nc=(input) 
        #base failure rate 
        lmda_base=1.25*(1000000/Nc)
        
        #Pressure multiplication factor
        if dP > 50: #in psi
            C_P=(dP/3000)**2

        #leakage multiplication factor
        if Qf>0.3: #units in in^3/min
            C_Q=(0.055)/Qf
        elif Qf<=0.3:
            C_Q= 4.2-(79*Qf)

        #Viscosity multiplication factor
        C_mu=(2*(10**(-8))/mu) #viscosity in lbf-min/in^2 

        #Fluid Contaminant multiplying factor


        #Spool clearnace multiplication factor
        
        if B>500: #units in microinch
            C_B=(B**2)/(6*(10**5))
        elif B<=500:
            C_B= 0.42
       
        #Spool Dia multiplication factor
        C_DS=0.615*DS #in inches


        #friction coefficiton multipying factor
        C_nu=nu    #friction Coefficient 

        #surface finish multiplication factor    
        #C_F=((f**1.65)/353) #surface finish in microns  


        #Contact pressure multiplication factor
        # S_s= #contact pressure lb/in^2    
        #C_S=0.26*((9000/S_s)**1.5) #surface finish in microns

        #surface finish multiplication factor    
        # Ds= #seat diameter inches
        #C_DT=(1.1*Ds)+0.32 #surface finish in microns

        #Land width multiplication factor    
        # L_T=  #land width in 
        #if L_T <= 0.34: #units in F
        #    C_SW = 3.55 - 24.52* L_T + 72.99 *(L_T**2) - 85.75 *(L_T**3)
        #elif L_T > 0.34:
        #    C_SW = 0.25
    
    #Flowrate multiplication factor
        # Fr_actual= #(panda pipes
        # Fr_rated= #user input
        C_w=1+(Fr_actual/Fr_rated)**2 #viscosity in lbf-min/in^2 
        return lmda_base*C_P*C_Q*C_mu*C_B*C_DS*C_nu*C_w
    
    for key, value in valve_data.items():
        # valve(valve_data[] = float(value))
        result=valve(
        Nc=float(value['Nc']),    
        dP=float(value['dP']),
        Qf=float(value['Qf']),
        mu=float(value['mu']),
        B=float(value['B']),
        DS=float(value['DS']),
        nu=float(value['nu']),
        Fr_actual=float(value['Fr_actual']),
        Fr_rated=float(value['Fr_rated']),
        

        )
    
    print("Result:", result)
    return jsonify(result)

@app.route('/api/pumpmtbfdata', methods=['POST'])
def pump_mtbf_data():
    pump_data=request.json
    print("sucess",pump_data)
    def lambda_fluid_driver(lamda_be_b, casing, Q, Qr,Vo,Vd,Fac):
            lamda_be_b = lamda_be_b*(10**-6)
            if casing=="Ordinary volute":
                if (0.1 <= Q/Qr <= 1.0) : Cpf = (9.94) - (0.90*(Q/Qr)) - (10.00*((Q/Qr)**2)) + (1.77*((Q/Qr)**2))   #Q, Qr, in gpm 
                elif (1.0 < Q/Qr < 1.1) : Cpf = 1.0 
                elif (1.1 <= Q/Qr <= 1.7) : Cpf = (-30.60) + (36*(Q/Qr)) - (4.50*((Q/Qr)**2)) - (2.20*((Q/Qr)**3))  
            elif casing == "Modified volute":
                Cpf = 5.31 - 0.55*(Q/Qr) - 12.00*((Q/Qr)**2) + 12.60*((Q/Qr)**3) - 4.63*((Q/Qr)**4) + 0.68*((Q/Qr)**5)
            elif casing == "Double volute":
                Cpf = 1.03 - 0.30*(Q/Qr) + 0.04*(Q/Qr)**2
            elif casing == "Displacement pumps":
                Cpf = 0.80 + 1.1*(Q/Qr)
            Cps=5 * ((Vo/Vd)**1.3)
            Cc=0.6+(0.05*Fac)
            Csf=1.25
            return lamda_be_b*Cpf*Cps*Cc*Csf

    def lamda_bearing(Ls,La,Vo,Vl,CW,To,diameter_b, particle_size,bearing_type):
            if(bearing_type=="Roller Bearing"):
                y=3.3
            elif(bearing_type=="Ball Bearing"):
                y=3.0

            R=90
            #lamda_be, failures/million hours
            # L10h = (10^6/60n)*((Ls/La)**y) 
            L10h = (10**6/60)*((Ls/La)**y)
            be_b = 1/L10h
            #failure rate adjusted to include actual dynamic load
            Cr = 0.223/(math.log(100/R))**2/3
            Cv = (Vo/Vl)**0.54 #Vo/Vl derived from graph 
            #Vo, lb-min/in^2
            #Vl, lb-min?in^2

            #For bearings designed for water based lubricants, CW = 0, Ccw = 1.00
            if CW < 0.8 : Ccw = 1.0 + 25.50*CW - 16.25*CW**2 
            elif CW > 0.8 : Ccw = 11.00

            Cy = (La/Ls)**y   #La/Ls derived from graph

            #La, lbf
            #Ls, lbf
            #y=3 for ball bearings, 3.3 for roller bearings

            if To < 183 : Ct = 1.0            #Temp in ℃ 
            if To > 183 : Ct = (To/183)**3    #Temp in ℃ 

            Csf = 1.0 #for both ball and roller bearing assuming uniform and steady load, free from shock 

            if (diameter_b <= 100): #in mm, 100mm
                if (particle_size <= 10) : Cc = 1.4  #particle size in microns, 10um (high cleanliness, oil filtered through fine filter)
                elif (particle_size > 10) : Cc = 2.5 #slight contamination in lubricant, hard particles

            elif (diameter_b > 100): #in mm, 100mm
                if (particle_size <= 10) : Cc = 1.2  #only high cleanliness & slight contamination bc no micron size given for other conditions
                elif (particle_size > 10) : Cc = 2.0 

            return be_b*Cr*Cv*Ccw*Ct*Csf*Cc
        
    def lambda_seal(Ps,Qf,Dsl,M,C,F,V,Tr,To,C0,Fr):

            lamda_seal_b = 22.8 #failures/million hours 

            if Ps <= 1500: Cp = 0.25           #Ps, lbs/in^2
            elif Ps > 1500: Cp = (Ps/3000)**2

            if Qf > 0.03 : Cq = 0.055/Qf    #Leakage, in^3/min   
            elif Qf <= 0.03 : Cq = 4.2 - (79*Qf)
    
            if F <= 15: Cf = 0.25 
            elif F > 15: Cf = (F**1.65)/353

            Cdl=1.1*Dsl+0.32

            Ch = ((M/C)/0.55)**4.3

            Vo=2*(1/(10**8)) 
            Cv=(Vo/V)
            if (Tr-To) <= 40 : 
                t = (Tr-To)/18
                Ct = 1/(2**t) 
            elif (Tr-To) > 40 : Ct = 0.21 

            C10 = 10     #in microns 
            N10 = 0.019
            Cn = (C0/C10)**3*Fr*N10

            return lamda_seal_b*Cq*Cp*Cdl*Ch*Cf*Cv*Ct*Cn

    def lambda_shaft(shaft_values_list,shaft_type):
            
            sh_b = 1/(10**6)
            
            if shaft_type=="Ground Shaft":
                Cf=0.89
            elif shaft_type=="Polished Shaft":
                Cf=1
            elif shaft_type=="Hot Rolled Shaft":
                Cf = (0.94 - (0.0046 + ((8.37 * (shaft_values_list[1])**2) * (10**6))))
            
            if shaft_values_list[0] > 160: 
                Ct = (460+shaft_values_list[0])/620
            elif shaft_values_list[0] <= 160:
                Ct = 1

            return sh_b*Cf*Ct
    for pump_id, data in pump_data.items():
        # Process bearing data
        bearing_data = data['bearingData']
        bearing_result = lamda_bearing(
            Ls=float(bearing_data['Ls']),
            La=float(bearing_data['La']),
            Vo=float(bearing_data['Vo']),
            Vl=float(bearing_data['Vl']),
            CW=float(bearing_data['Cw']),
            To=float(bearing_data['T']),
            diameter_b=float(bearing_data['BearingDiameter']),
            particle_size=float(bearing_data['Particle_size']),
            bearing_type=bearing_data['bearingType']
        )

        fluid_data=data['fluidData']
        fluid_result=lambda_fluid_driver(lamda_be_b=float(fluid_data['fluid_driver']),
            casing=fluid_data['casings_options'],
            Q=float(fluid_data['Q']),
            Qr=float(fluid_data['Qr']),
            Vo=float(fluid_data['Vo']),
            Vd=float(fluid_data['Vd']),
            Fac=float(fluid_data['Fac'])
        )
        # Process seal data
        seal_data = data['sealData']
        seal_result = lambda_seal(
            Ps=float(seal_data['Ps']),
            Qf=float(seal_data['Qf']),
            Dsl=float(seal_data['Dsl']),
            M=float(seal_data['M']),
            C=float(seal_data['C']),
            F=float(seal_data['F']),
            V=float(seal_data['V']),
            Tr=float(seal_data['TR']),
            To=float(seal_data['To']),
            C0=float(seal_data['C0']),
            Fr=float(seal_data['Fr'])
        )

        # Process shaft data
        shaft_data = data['shaftData']
        shaft_result = lambda_shaft(
            shaft_values_list=[float(shaft_data['TAT']), float(shaft_data['TS'])],
            shaft_type=shaft_data['shaftSurfaceOptions']
        )

        # Here you can do something with the results
    print(f"{pump_id} - Bearing Result: {bearing_result}, Seal Result: {seal_result}, Shaft Result: {shaft_result}, Fluid result: {fluid_result}")

    result=1/(bearing_result+seal_result+shaft_result+fluid_result)
    return jsonify(result)

@app.route('/api/cost-data', methods=['POST'])
def receive_cost_data():
    data = request.json
    print(data)
    nodes = data.get('nodes')
    nodeDetails=data.get('nodeDetails')
    print(nodeDetails)
    if not nodes:
        return jsonify({"ALERT": "No connection between blocks"})
    nodeDetails_df = pd.DataFrame(nodeDetails)
    nodeDetails_df = pd.DataFrame.from_dict(nodeDetails, orient='index').reset_index()

    if(nodeDetails_df.empty):
        pass
    else:
        nodeDetails_df.columns = ['id', 'reliability', 'mtbf', 'mttr']
        
        # Calculate Availability for each node
        nodeDetails_df['availability'] = nodeDetails_df['mtbf'] / (nodeDetails_df['mtbf'] + nodeDetails_df['mttr'])

        # Keep only necessary columns
        nodeDetails_df = nodeDetails_df[['id', 'reliability', 'availability','mtbf','mttr']]
    print("nodeDetails",nodeDetails_df)
    data = []
    # print("nodeDetals_df",nodeDetails_df)
    for node in nodes:
        print("node",node['id'])
        if nodeDetails_df.empty:
            node_info = {'reliability': 1, 'availability': 1}
        else:
            node_info = nodeDetails_df[nodeDetails_df['id'] == node['id']].iloc[0].to_dict()
        data.append({
            'RBD_Label': node['id'],
            'Reliability': node_info['reliability'],
            'Availability': node_info['availability'],
            'MTBF': node_info['mtbf'],
            'MTTR': node_info['mttr']
        })
    df=pd.DataFrame(data)
    nodes_data = pd.DataFrame(nodes)
    print("Nodes data",nodes_data['id'])
    # nodes_data= pd.DataFrame.from_dict(nodes_data, orient='index').reset_index()
    # print("node",nodes_data)
    # Create a DataFrame
    # df = pd.DataFrame({'RBD Label': nodes_data['id'],"Reliability":,"Availability":})

    # Save the DataFrame to an Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return send_file(output, download_name='rbd_label.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)