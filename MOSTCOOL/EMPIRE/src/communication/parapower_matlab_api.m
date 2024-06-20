function parapower_matlab_api(input_json_path, output_json_path)
    clearvars -except input_json_path output_json_path
    % Add the path to the ParaPower_Software folder
    addpath('../ParaPower_Software');
    
    configFile = fileread(input_json_path);
    config = jsondecode(configFile);

    addMaterials(input_json_path);
    TSRM = definePPTCM(input_json_path);
    TSRM_MI = FormModel(TSRM);

    % Visualize Original Model Before simulation
    figure;
    PlotTitle = 'TSRM Pre-Simulation';
    Visualize(PlotTitle, TSRM_MI, 'ShowQ');
    
    % Perform the specified type of analysis
    if strcmpi(config.analysis.type, 'thermal')
        if strcmpi(config.analysis.mode, 'static')
            resobj = thermal_static(TSRM_MI);
        elseif strcmpi(config.analysis.mode, 'transient')
            resobj = thermal_transient(TSRM_MI);
        end
    elseif strcmpi(config.analysis.type, 'stress')
        if strcmpi(config.analysis.StressMode, 'Hsueh')
            resobj = stress_static(TSRM_MI, 'Hsueh');
        elseif strcmpi(config.analysis.StressMode, 'NonDirectional')
            resobj = stress_static(TSRM_MI, 'NonDirectional');
        end
    end

    resobj.Model.FeatureDescr = TSRM_MI.FeatureDescr;
    resobj.Model.FeatureMatrix = TSRM_MI.FeatureMatrix;

    % Results preparation
    res_struct = struct('feature', {}, 'time', {}, 'temperature', {}, 'stress', {});
    
    if strcmpi(config.results.type, 'global') & strcmpi(config.analysis.type, 'thermal')
        [time, res] = get_global_max(resobj, config.analysis.type);
        res_struct(1).feature = 'global';
        res_struct(1).time = time;
        res_struct(1).temperature = res;
    elseif strcmpi(config.results.type, 'global') & strcmpi(config.analysis.type, 'stress')
        [time, res] = get_global_max(resobj, 'Stress');
        res_struct(1).feature = 'global';
        res_struct(1).time = time;
        res_struct(1).stress = res;
    elseif strcmpi(config.results.type, 'individual') & strcmpi(config.analysis.type, 'thermal')
        for i = 1:length(TSRM_MI.FeatureDescr)
            [time, res] = get_max_by_feature(resobj, TSRM_MI.FeatureDescr{i}, config.analysis.type);
            res_struct(i).feature = TSRM_MI.FeatureDescr{i};
            res_struct(i).time = time;
            res_struct(i).temperature = res;
        end
    elseif strcmpi(config.results.type, 'individual') & strcmpi(config.analysis.type, 'stress')
        for i = 1:length(TSRM_MI.FeatureDescr)
            [time, res] = get_max_by_feature(resobj, TSRM_MI.FeatureDescr{i}, config.analysis.type);
            res_struct(i).feature = TSRM_MI.FeatureDescr{i};
            res_struct(i).time = time;
            res_struct(i).stress = res;
        end
    end

    % Convert results to JSON with 'PrettyPrint' option
    strResults = jsonencode(res_struct, 'PrettyPrint', true);

    % Post-process JSON to compact arrays onto a single line
    strResults = regexprep(strResults, '\[\s*([^\[\]]*?)\s*\]', '[$1]');
    strResults = regexprep(strResults, ',\s*\n\s*', ', ');

    % Write the JSON to file
    fid = fopen(output_json_path, 'w');
    fwrite(fid, strResults, 'char');
    fclose(fid);
    
    % Define the path to the temporary material library file in the same folder as the original file
    temporaryMaterialFile = fullfile('../ParaPower_Software', 'TemporaryMaterials.mat');
    % Delete the temporary file
    delete(temporaryMaterialFile);
end

function addMaterials(configFilePath)
    % Important:
    %           Use SI Units
    %
    % Purpose:
    %           This function adds a new material to the existing ParaPower Thermal Simulation
    %           Material Library (MatLib) based on a JSON configuration file. It supports
    %           adding Solid, Phase Change Material (PCM), and Internal Boundary Condition (IBC)
    %           materials with specified properties in SI units.
    %
    % Inputs:
    %           Material Types and Properties (units in parentheses):
    %           Solid ("solid"):
    %                           name (String): Name of the material.
    %                           cte (1/K): Coefficient of Thermal Expansion.
    %                           E (Pa): Young's Modulus.
    %                           nu (dimensionless): Poisson's Ratio.
    %                           k (W/(m·K)): Thermal Conductivity.
    %                           rho (kg/m^3): Density.
    %                           cp (J/(kg·K)): Specific Heat Capacity.
    %
    %           Phase Change Material ("pcm"): Includes all Solid properties plus:
    %                           k_l (W/(m·K)): Liquid Conductivity.
    %                           rho_l (kg/m^3): Liquid Density.
    %                           cp_l (J/(kg·K)): Liquid Specific Heat.
    %                           lf (J/kg): Latent Heat of Fusion.
    %                           tmelt (°C): Melting Temperature.
    %
    %           Internal Boundary Condition ("ibc"):
    %                           name (String): Name of the material.
    %                           h_ibc (W/(m^2·K)): Heat Transfer Coefficient.
    %                           T_ibc (°C): Temperature.
    %
    % Outputs:
    %           This function does not return any value but updates and saves the 'MatLib' object
    %           in 'DefaultMaterials.mat' with the new material based on the provided configuration.

    % Add the path to the ParaPower_Software folder
    addpath('../ParaPower_Software');
    
    % Define the path to the original material library file in the ParaPower_Software folder
    originalMaterialFile = fullfile('../ParaPower_Software', 'DefaultMaterials.mat');
    
    % Define the path to the temporary material library file in the same folder as the original file
    temporaryMaterialFile = fullfile('../ParaPower_Software', 'TemporaryMaterials.mat');
    
    % Copy the original material library file to a new file in the same folder
    copyfile(originalMaterialFile, temporaryMaterialFile);
    
    % Load the temporary material library file
    load(temporaryMaterialFile, 'MatLib');

    
    % Read and decode the JSON configuration file.
    configFile = fileread(configFilePath);
    jsonData = jsondecode(configFile);
    
    % Ensure the "materials" key exists and extract material array.
    if isfield(jsonData, 'materials')
        materialsArray = jsonData.materials;
    else
        error('The JSON file does not contain a "materials" key.');
    end
    
    % Iterate over each material configuration in the materials array.
    for idx = 1:length(materialsArray)
        % Adjust for potential cell array structure from jsondecode
        if iscell(materialsArray)
            materialConfig = materialsArray{idx}; % Cell array indexing
        else
            materialConfig = materialsArray(idx); % Standard structure array indexing
        end
        
        % Extract material type and convert to lower case for consistency.
        materialType = lower(materialConfig.type);
        
        % Initialize an empty cell array for properties.
        props = {};
        
        % Handle each material type specifically.
        switch materialType
            case 'solid'
                requiredProps = {'name', 'cte', 'E', 'nu', 'k', 'rho', 'cp'};
            case 'pcm'
                requiredProps = {'name', 'cte', 'E', 'nu', 'k', 'rho', 'cp', 'k_l', 'rho_l', 'cp_l', 'lf', 'tmelt'};
            case 'ibc'
                requiredProps = {'name', 'h_ibc', 'T_ibc'};
            otherwise
                error('Unknown material type: %s', materialType);
        end
        
        % Verify that all required properties are present and not NaN.
        for propName = requiredProps
            propName = propName{1}; % Convert cell to string for indexing
            if ~isfield(materialConfig, propName)
                error('Material #%d (%s) is missing required property "%s".', idx, materialType, propName);
            end
            propValue = materialConfig.(propName);
            if isnan(propValue)
                error('Material #%d (%s) has invalid value for property "%s".', idx, materialType, propName);
            end
            props{end+1} = propName; % Add property name
            props{end+1} = propValue; % Add property value
        end
        
        % Debug statement to print the material properties
        disp(['Adding material #' num2str(idx) ': ' materialConfig.name]);
        disp(materialConfig);
        
        % Create the material object based on its type and properties.
        switch materialType
            case 'solid'
                materialObj = PPMatSolid(props{:});
            case 'pcm'
                materialObj = PPMatPCM(props{:});
            case 'ibc'
                materialObj = PPMatIBC(props{:});
            otherwise
                error('Unhandled material type: %s', materialType);
        end
        
        % Add the new material to the library.
        MatLib.AddMatl(materialObj);
    end
    
    % Save the updated library to the copied file.
    save(temporaryMaterialFile, 'MatLib');
    disp('Material library updated with multiple materials.');
    MatLib.ShowTable

end

function model = definePPTCM(configFilePath)

    % Purpose:
    %           Configures a PPTCM based on a JSON configuration file by dynamically assigning external conditions,
    %           model features, simulation parameters, and potting material based on provided specifications.
    %
    % Inputs:
    %           ExternalConditions: Defines the thermal interaction of the model with its environment.
    %                     - h_Xminus: Heat transfer coefficient on the negative X face (W/(m^2·K))
    %                     - h_Xplus: Heat transfer coefficient on the positive X face (W/(m^2·K))
    %                     - h_Yminus: Heat transfer coefficient on the negative Y face (W/(m^2·K))
    %                     - h_Yplus: Heat transfer coefficient on the positive Y face (W/(m^2·K))
    %                     - h_Zminus: Heat transfer coefficient on the negative Z face (W/(m^2·K))
    %                     - h_Zplus: Heat transfer coefficient on the positive Z face (W/(m^2·K))
    %                     - Ta_Xminus: Ambient temperature on the negative X face (°C)
    %                     - Ta_Xplus: Ambient temperature on the positive X face (°C)
    %                     - Ta_Yminus: Ambient temperature on the negative Y face (°C)
    %                     - Ta_Yplus: Ambient temperature on the positive Y face (°C)
    %                     - Ta_Zminus: Ambient temperature on the negative Z face (°C)
    %                     - Ta_Zplus: Ambient temperature on the positive Z face (°C)
    %                     - Tproc: Processing temperature (°C)
    %           Features: Defines the physical characteristics and material properties of the model.
    %                     - x: X-coordinates defining the model geometry (m)
    %                     - y: Y-coordinates defining the model geometry (m)
    %                     - z: Z-coordinates defining the model geometry (m)
    %                     - Matl: Material name (String)
    %                     - Q: Heat source (W or W/m^3)
    %                     - dx: Divisions in X for meshing (dimensionless, number of divisions)
    %                     - dy: Divisions in Y for meshing (dimensionless, number of divisions)
    %                     - dz: Divisions in Z for meshing (dimensionless, number of divisions)
    %                     - Desc: Description of the feature (String)
    %           Params: Defines the simulation parameters.
    %                     - Tinit: Initial temperature (K or °C)
    %                     - DeltaT: Time step (s)
    %                     - Tsteps: Number of time steps (dimensionless, number of steps)
    %
    % Outputs:
    %           No explicit return values. Initializes a PPTCM with configuration from the JSON file.
    
    % Add the path to the ParaPower_Software folder
    addpath('../ParaPower_Software');
    % Define the path to the temporary material library file in the same folder as the original file
    temporaryMaterialFile = fullfile('../ParaPower_Software', 'TemporaryMaterials.mat');
    % Load the teporary material library.
    load(temporaryMaterialFile, 'MatLib');
    
    % Read and decode the JSON configuration file.
    configFile = fileread(configFilePath);
    configData = jsondecode(configFile);

    % Instantiate the PPTCM class.
    model = PPTCM();
    
    % Assign the material library.
    model.MatLib = MatLib;

    % PottingMaterial handling
    if isfield(configData, 'PottingMaterial')
        model.PottingMaterial = configData.PottingMaterial;
    else
        model.PottingMaterial = 0; % If Material is 0, then the space is empty.
    end

    % Dynamically assign properties from configData for ExternalConditions and Params
    configMaps = struct(...
                        'ExternalConditions', {{'h_Xminus', 'h_Xplus', 'h_Yminus', 'h_Yplus', 'h_Zminus', 'h_Zplus', ...
                                               'Ta_Xminus', 'Ta_Xplus', 'Ta_Yminus', 'Ta_Yplus', 'Ta_Zminus', 'Ta_Zplus', 'Tproc'}}, ...
                        'Features', {{'x', 'y', 'z', 'Matl', 'Q', 'dx', 'dy', 'dz', 'Desc'}}, ...
                        'Params', {{'Tinit', 'DeltaT', 'Tsteps'}});
                                                
    % Assign ExternalConditions and Params
    fieldNames = fieldnames(configMaps);
    for i = 1:length(fieldNames)
        fieldName = fieldNames{i};
        if isfield(configData, fieldName) && ~strcmp(fieldName, 'Features')
            props = configMaps.(fieldName);
            for j = 1:length(props)
                prop = props{j};
                if isfield(configData.(fieldName), prop)
                    model.(fieldName).(prop) = configData.(fieldName).(prop);
                end
            end
        end
    end

    % Handling multiple features from "features" key
    if isfield(configData, 'features')
        % Direct assignment if featuresData is a structure array
        model.Features = configData.features; % Assuming featuresData matches the expected structure array format for model.Features
    else
        error('The JSON file does not contain a "features" key.');
    end

    disp('PPTCM has been successfully defined and configured according to the JSON configuration.');
end

function resobj = thermal_static(model)
    InitTime = [];
    StepsToEstimate = 0;
    ComputeTime = [];

    S1 = scPPT('MI', model);
    setup(S1, []);
    tic;
    [Tprnt, T_in, MeltFrac, MeltFrac_in] = S1([InitTime ComputeTime(1:min(StepsToEstimate, length(ComputeTime)))]);

    if length(ComputeTime) > StepsToEstimate
        [Tprnt2, T_in2, MeltFrac2, MeltFrac_in2] = S1(ComputeTime(3:end));
        Tprnt = cat(4, T_in, Tprnt, Tprnt2);
        MeltFrac = cat(4, MeltFrac_in, MeltFrac, MeltFrac2);
    else
        Tprnt = cat(4, T_in, Tprnt);
        MeltFrac = cat(4, MeltFrac_in, MeltFrac);
    end

    TSRM_MI = struct('GlobalTime', [InitTime ComputeTime], 'FeatureMatrix', model.FeatureMatrix); 

    TSRM_MI.Model = TSRM_MI;

    Results = PPResults(now, TSRM_MI, 1, 'Thermal', 'MeltFrac');

    Results = Results.setState('Thermal', Tprnt, '°C');
    Results = Results.setState('MeltFrac', MeltFrac, '%');
    resobj = Results;
end

function resobj = stress_static(model, stressModelName)
    tic;
    if ~isempty(model.GlobalTime)
        InitTime = model.GlobalTime(1);
        ComputeTime = model.GlobalTime(2:end);
        model.GlobalTime = InitTime;
        StepsToEstimate = 2;
    else
        InitTime = [];
        StepsToEstimate = 0;
        ComputeTime = [];
    end

    S1 = scPPT('MI', model);
    setup(S1, []);
    tic;
    [Tprnt, T_in, MeltFrac, MeltFrac_in] = S1([InitTime ComputeTime(1:min(StepsToEstimate, length(ComputeTime)))]);

    model.GlobalTime = [InitTime ComputeTime];
    EstTime = toc;

    S_Results(1) = PPResults(now, model, 1, 'Thermal', 'MeltFrac');
    S_Results(1) = S_Results(1).setState('Thermal', Tprnt, '°C');
    S_Results(1) = S_Results(1).setState('MeltFrac', MeltFrac, '%');

    addpath('./Stress_Models/');
    switch stressModelName
        case 'Hsueh'
            stress_results = Stress_Hsueh(S_Results(1));
        case 'NonDirectional'
            stress_results = Stress_NonDirectional(S_Results(1));
        otherwise
            error('Unknown stress model: %s', stressModelName);
    end

    % Create a 4D array to hold stress components
    stressArray = NaN * ones(size(stress_results.X, 1), size(stress_results.X, 2), size(stress_results.X, 3), 4);
    stressArray(:,:,:,1) = stress_results.X;
    stressArray(:,:,:,2) = stress_results.Y;
    stressArray(:,:,:,3) = stress_results.Z;
    stressArray(:,:,:,4) = stress_results.VM;

    % Ensure that NaNs are handled if Z is not provided
    if isfield(stress_results, 'Z')
        stressArray(:,:,:,3) = stress_results.Z;
    else
        stressArray(:,:,:,3) = NaN; % If Z stress is not applicable
    end

    S_Results(1) = S_Results(1).addState('Stress', stressArray, 'Pa'); % Assuming stress is in Pascals

    resobj = S_Results;
end

function [time, results] = get_global_max(ResultsObject,result_type)
time = ResultsObject.Model.GlobalTime;
if isempty(time)
    time = [0 0];
end
temporary_results = zeros(1,length(time));
results_data = ResultsObject.getState(result_type);
for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
    if strcmpi(result_type, 'thermal')
        temporary_results(j) = max(results_data_slice, [], 'all');
    % Stress?
    else
        temporary_results(j) = max(abs(results_data_slice), [], 'all');
    end
end
results = temporary_results;
end

function [time, results] = get_max_by_feature(ResultsObject, feature_name, result_type)
FeatureDescr = ResultsObject.Model.FeatureDescr;
time = ResultsObject.Model.GlobalTime;
if isempty(time)
    time = [0 0];
end
ind = 0;
for i = 1:length(FeatureDescr)
    current_item = FeatureDescr(i);
    current_name = current_item{1};
    if strcmp(feature_name, current_name)
        ind = i;    
    end
end
feat_ind = find(ResultsObject.Model.FeatureMatrix == ind);
temporary_results = zeros(1,length(time));
results_data = ResultsObject.getState(result_type);
for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
	temporary_results(j) = max(results_data_slice(feat_ind));     
end
results = temporary_results;
end
