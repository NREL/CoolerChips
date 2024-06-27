% Example ParaPower Model Script
clear
Desc='PP_script_tutorial';  %Description of the model

%% Define script parameters
% The parapower solver does not enforce a particular unit convention, but
% material property definition fields are labeled (but not enforced) in SI units.  To avoid
% confunsion SI is recommended.

base_x = 5e-2;  % [m]
base_y = base_x;
base_z = 5e-3;

chip_x = 1e-2;
chip_y = chip_x;
chip_z = 500e-6;

chip_flux=100e4;  %100 W/cm^2, a modest power level

% For many thermal analyses, relative temperature is fine (e.g. set ambient to zero)
% Phase change material melt temperatures are by convention in deg C in
% material library, so in a model with PCM you will typically work in
% absolute C.

T_ambient=25;
fin_wall_htc=200; % [W/m^2-K]

N_fins = [6, 10, 20];  
fin_length = [1, 2, 4]*1e-2;
% we will demonstrate two approaches to parametric analyses...
% 1) explicit parametric loop in script (using N_fins)
% 2) model expansion using PPTCM methods (what the GUI performs),
%       using fin_length and fin material

% PPTCM expands parametric material assignments to each feature
% indepedently.  Since we define below a heatsink baseplate and the
% collection of heatsink fins as two features, we can end up with different
% materials for the baseplate and finstock.

% total # simulations will be l(N_fins) * l(fin_length) * l(HeatsinkMatl)

%% Define Materials
% Some very superfluous steps here to demonstrate different approaches

load 'DefaultMaterials.mat'  %load the default MatLib object from ParaPower directory
OldMatLib=MatLib.CreateCopy;  %copy the loaded libary object to a new name.
clear MatLib

NewMatLib=PPMatLib;  %create a blank material library from scratch

NewMatLib.AddMatl(OldMatLib.GetMatName('Cu'));  %pull copper by name from Defaults
NewMatLib.AddMatl( PPMatSolid('name'  , 'Al'  ...
                           ,'cte'   , 2.4e-5...
                           ,'E'     , 1.1e11...
                           ,'nu'    , .37   ...
                           ,'k'     , 172   ...
                           ,'rho'   , 2700  ...
                           ,'cp'     , 900   ...
                        )) ;                      %add aluminum from scratch
NameList=OldMatLib.GetParam('Name');              %pull all the material names out of the defaults
SiC_index=find(strcmpi('SiC',NameList));          %search for SiC
if isempty(SiC_index)
    error('Someone deleted silicon carbide from the default materials!')
end
SiC_mat_obj=OldMatLib.GetMatNum(SiC_index);        %extract the SiC PPMatSolid obj so you can look at it
NewMatLib.AddMatl(SiC_mat_obj);                    %add it in as a material

NewMatLib.AddMatl(OldMatLib.GetMatName('NoMatl')); %this is a material we use by convention for 2D heat sources
NoMatl_2=OldMatLib.GetMatName('NoMatl');
NoMatl_2.Name='NoMatl_2';
NewMatLib.AddMatl(NoMatl_2);

NewMatLib.AddMatl( PPMatIBC('name', 'ForcedAir', ... %add a convection boundary material
                            'h_ibc', fin_wall_htc, ...
                            'T_ibc', T_ambient));
                        
NewMatLib.AddMatl( PPMatMaterialList('name','HeatsinkMatl','MatList','Cu,Al'));
%Define a "supermaterial" that parameterizes over material choice

%can review the material library with the command line input NewMatLib.ShowTable

%% Define TCM model object
TestCaseModel=PPTCM;  %PPTCM is the high-level model description object that corresponds to the GUI entries
TestCaseModel.MatLib=NewMatLib;  %set the material library property of the model
TestCaseModel.VariableList={'fin_length',['[' num2str(fin_length) ']'];'base_z',['[' num2str(base_z) ']']};
% define fin_length as a TCM parameter with multiple values
% include base_z as a scalar TCM parameter to make life convenient

% the VariableList property corresponds to the Parameters dialog in the
% GUI.  It wants to be a nx2 cell array of strings.

%% Define Boundary and Timing GUI entries
TestCaseModel.ExternalConditions.h_Xminus=fin_wall_htc;
TestCaseModel.ExternalConditions.h_Xplus =fin_wall_htc;
TestCaseModel.ExternalConditions.h_Yminus=fin_wall_htc;
TestCaseModel.ExternalConditions.h_Yplus =fin_wall_htc;
TestCaseModel.ExternalConditions.h_Zminus=fin_wall_htc;  %this is the fin tips
TestCaseModel.ExternalConditions.h_Zplus =0;   %insulated boundary on top of chip

TestCaseModel.ExternalConditions.Ta_Xminus=T_ambient;
TestCaseModel.ExternalConditions.Ta_Xplus =T_ambient;
TestCaseModel.ExternalConditions.Ta_Yminus=T_ambient;
TestCaseModel.ExternalConditions.Ta_Yplus =T_ambient;
TestCaseModel.ExternalConditions.Ta_Zminus=T_ambient;
TestCaseModel.ExternalConditions.Ta_Zplus =T_ambient;

TestCaseModel.ExternalConditions.Tproc=T_ambient; %Processing temperature, used for stress analysis

TestCaseModel.Params.Tinit     = T_ambient;  %Initial temperature of all materials
TestCaseModel.Params.DeltaT    = .1; %Time step size, in seconds
TestCaseModel.Params.Tsteps    = 10; %Number of time steps.
%We will be doing a steady analysis, so we won't be using these

TestCaseModel.PottingMaterial  = 0;  %Material that surrounds features 
%in each layer as defined by text strings in matlibfun. 
%If Material is 0, then the space is empty and not filled by any material.


%% Build Features structure
% Define a structure array that has the fields corresponding to the GUI feature
% table.  The feature xyz dimensions are a vector, rather than two seperate
% fields

Features=TestCaseModel.Features;
% mimic the structure of the empty PPTCM features property.
% this isn't strictly necessary...just don't mess up below

Features(1).Desc='Chip';
Features(1).x=[-1 1]*chip_x/2; %centering chip at implied origin
Features(1).y=[-1 1]*chip_y/2;
Features(1).z=[0 chip_z];
Features(1).dx=3;
Features(1).dy=Features(1).dx;
Features(1).dz=3;
Features(1).Matl='SiC';
Features(1).Q=0;

Features(end+1,1).Desc='Chip_heater';  %extend array by one more, we want it vertical
Features(end).x=Features(end-1).x;
Features(end).y=Features(end-1).y;
Features(end).z=[chip_z chip_z];     %this features is 2D so zero thickness in Z
Features(end).dx=Features(end-1).dx;
Features(end).dy=Features(end-1).dy;
Features(end).dz=Features(end-1).dz;
Features(end).Matl='NoMatl';
Features(end).Q=chip_flux*chip_x*chip_y; %features want heat dissipation in W

Features(end+1).Desc='Heatsink_Base';
Features(end).x=[-1 1]*base_x/2; %centering base at implied origin
Features(end).y=[-1 1]*base_y/2;
Features(end).z=[-1 0]*base_z;
Features(end).dx=1;
Features(end).dy=9;
Features(end).dz=3;
Features(end).Matl='HeatsinkMatl';
Features(end).Q=0;

Features(end+1).Desc='Fin_root';    
%place a feature that will help postprocess later
Features(end).x=Features(end-1).x;
Features(end).y=Features(end-1).y;
Features(end).z=[-base_z -base_z];
Features(end).dx=1;
Features(end).dy=1;
Features(end).dz=1;
Features(end).Matl='NoMatl_2';    
%since this is zero thickness it doesn't matter what material
Features(end).Q=0;

Features(end+1).Desc='Heatsink_Fins';
Features(end).x=Features(end-1).x;
Features(end).y=Features(end-1).y;
Features(end).z={'-base_z-fin_length','-base_z'};
%TCM parameters need to be passed as strings
%for x, y, z, those strings need to be in a 1x2 cell array.
Features(end).dx=1;
Features(end).dy=1;
Features(end).dz='fin_length/2e-3'; %sets elements to be 2 mm long
Features(end).Matl='HeatsinkMatl';
Features(end).Q=0;

%% Parameterize by number of fins and expand other parameters

FinFeatures=TestCaseModel.Features; %blank feature structure to hold fin definition
fin_widths=base_x./(2*N_fins-1);

FinFeatures.y=Features(end).y;
FinFeatures.z=Features(end).z;
FinFeatures.dx=1;
FinFeatures.dy=1;
FinFeatures.dz=1;
FinFeatures.Matl='ForcedAir';
FinFeatures.Q=0;

TestCaseModel=repmat(TestCaseModel,[1 length(N_fins)]);
TCMlist=cell(1, length(N_fins));  %cell array to hold expanded cases
FinFeatures=repmat(FinFeatures,[max(N_fins)-1 length(N_fins)]); %this is unsual
%Features is normally an nx1 array, TCM is scalar
%but adding some extra columns will help us parameterize the number of fins 

%we are cutting gaps in the heatsink material, leaving behind fins
%  |x| |x| |x| ....
%  ^     ^
%  |     +fin_widths*(2n-1)
%  -base_x/2

for i=1:length(N_fins)         %This is explicit script parameterization         
    for n=1:N_fins(i)-1
        %this loop here is a good example of why to use a script
        %getting all these fins into the GUI table is a pain
        FinFeatures(n,i).Desc=['Fin_ibc_' num2str(n)];
        FinFeatures(n,i).x=[0 fin_widths(i)]+fin_widths(i)*(2*n-1)-base_x/2;
    end
    TestCaseModel(i).Features=[Features; FinFeatures(1:n,i)];
    %concatenate the basic features with the new fin features, and set the
    %PPTCM property.
    
    %We now have multiple "unexpanded" models
    
    TCMlist{i}=[TestCaseModel(i).GenerateCases]';
    %Expand the models using the PPTCM expansion method,
    %parameterizing across HeatsinkMatl and fin_length
    %want entries to be column vectors so we can horzcat.
end

TCMlist=horzcat(TCMlist{:});  %drop the cells and work with an obj array

%% Simulate each model

Results=cell(size(TCMlist));  %allocate some cell arrays to hold things
MIcell=Results;         %allocate
root_watts=MIcell;  %we want this for the postprocess section and 
                    %its much easier to get here since we throw away the
                    %sPPT during each loop iteration.  You could obviously
                    %store an array of sPPT objects and batch process if
                    %you care to use the memory.

for i=1:numel(TCMlist)  %this can easily be a parfor loop if the toolbox is available
        MIcell{i}=FormModel(TCMlist(i));  
        %form the selected high level model into the low level MI
        %description
        
        ThermalSim=sPPT('MI',MIcell{i});
        %initialize a thermal simulation sPPT object, setting the MI
        %property
        
        %the argument to run the simulation is the timestep vector.
        %inputting an empty vector entry flags the
        %simulation as a steady state solve.
        [Tout,Tin,PHout,PHin]=ThermalSim([]);
        % can also pass in [anynumber NaN] to flag ss
                
        %there are no PCMs, so initial and final meltfractions (PH) are
        %zero.  We also are not interested in Tin, which is just uniform
        %T_Ambient
        
        Results{i}=Tout;

        [root_watts{i},~]=ThermalSim.GetHeatFlow; %element surface watts
end

demo_result=randi(numel(TCMlist));  %select a random simulation from our set
[~,n_fin_chosen]=ind2sub(size(TCMlist),demo_result);  %grab column subscript from TCMlist
n_fin_chosen=num2str(N_fins(n_fin_chosen)); %which corresponds to how many fins
demo_params=TCMlist(demo_result).ParamVar;
GeomText=['Model to solve: ',demo_params{2,2},' baseplate with ',n_fin_chosen,' ',demo_params{3,2},' fins of length ',demo_params{1,2},' meters'];

figure(10);
Visualize(GeomText,MIcell{demo_result},'ShowQ');  %plot model geometry
%figure(11);  %comment out so we can plot with title info including fin efficiency
%Visualize('Steady State Temperature',MIcell{demo_result},'State',Results{demo_result});  %plot temperature

%% Postprocess
% One big reason to script an analysis is to do some very specific
% post-processing

% Recommend learning your way around the low-level MI model description
% structure
% MI.Model is a 3D array of elements with integer references to material numbers in
% MI.MatLib.  The results from the sPPT solver correspond to the centroids of these
% elements.

% We will calculate max and min fin efficiency for every model
% fin efficiency is the ratio of actual heat dissipated by a fin to that
% which would be dissipated by a fin of infinite conductivity.  
% We have spreading in the Y-dir, so we will modify this somewhat

%wetted area of different fins
%           fin ends at Y-, Y+       fin/channel sidewalls     fin tips at Z-
fin_areas=(2*fin_widths'*fin_length + 2*base_y*fin_length + base_y*fin_widths')';
% m x n =  [(n x 1)(1 x m)         +        (1 x m)    +        (n x 1)] transposed
%there is some implied repmat in the addition here, MATLAB stuff.
% m is selected from approriate fin_length, n is selected from N_fins

root_temps=cell(size(Results));     %allocating empty cell array
fin_eff=root_temps;                   %allocating empty cell array

for i=1:numel(root_temps)
   root_mat=find(strcmpi('NoMatl_2',MIcell{i}.MatLib.GetParam('Name')));
   %grab the material number we want
   root_mask=MIcell{i}.Model==root_mat;
   root_area_temp=Results{i}(root_mask);
   root_area_temp=reshape(root_area_temp,[length(MIcell{i}.X) length(MIcell{i}.Y)]);
   %mask into the results to get just the temperatures we want
   
   root_areas=imag(MIcell{i}.VA(root_mask));
   root_areas=reshape(root_areas,[length(MIcell{i}.X) length(MIcell{i}.Y)]);
   %MI.VA contains element volumes (for 3D) and areas (for 2D).  
   %They are stored as complex numbers so you can distinguish the two
   
   root_avg_temp=root_area_temp.*root_areas; %area weighting

   fin_plan=MIcell{i}.Model(:,:,1);
   %we want to add up all the elements within each fin, but we need to
   %figure out what elements go with what fin.
   
   fin_plan(fin_plan==find(strcmpi('ForcedAir',MIcell{i}.MatLib.GetParam('Name'))))=0;
   fin_plan=fin_plan~=0;
   root_avg_temp(~fin_plan)=0;  %zero out temperatures we dont want
   root_areas(~fin_plan)=0;
   
   for x=flip(1:size(fin_plan,1)-1) %count down starting at end-1
       if fin_plan(x,1) && fin_plan(x+1,1)  %if this row and one higher are both fin material
           root_areas(x,:)=root_areas(x,:)+root_areas(x+1,:); %add them together
           root_areas=[root_areas(1:x,:); root_areas(x+2:end,:)]; %and drop the extra one
           root_avg_temp(x,:)=root_avg_temp(x,:)+root_avg_temp(x+1,:); %add them together
           root_avg_temp=[root_avg_temp(1:x,:); root_avg_temp(x+2:end,:)]; %and drop the extra one 
       end
   end
   
   root_avg_temp=sum(root_avg_temp,2);
   root_avg_temp=root_avg_temp(root_avg_temp~=0);
   root_areas=sum(root_areas,2);
   root_areas=root_areas(root_areas~=0);
   
   root_temps{i}=root_avg_temp./root_areas;  %area weighted average of each fin's root temperature
   %this became ridiculous by the end.
   
   root_z_loc=find(sum(root_mask,[1 2]))-1;  %we need the first 3D elements at the base of the fins
   %so we find the NoMatl2 z-index and count down 1
   sumY_root_watts=-1.*sum(root_watts{i}.z_plus(:,:,root_z_loc),2); %we pick z_plus to we get the watts coming from NoMatl2 into the fins
   %and sum the power along the Y-dir of each fin
   [~,which_N_fins]=ind2sub(size(TCMlist),i); 
   sum_root_watts=zeros(N_fins(which_N_fins),1); %allocate a vector with entries for each fin
   k=1;
   for j=1:length(sumY_root_watts)-1 %some fins have multiple elements in X-dir
       sum_root_watts(k)=sumY_root_watts(j)+sum_root_watts(k);
       if sumY_root_watts(j+1)==0 && sumY_root_watts(j)~=0 %detect a falling edge
           k=k+1; %move to next fin
       end
   end
   sum_root_watts(k)=sumY_root_watts(end)+sum_root_watts(k); %grab that last entry not covered in loop
   
   which_fin_length=find(fin_length==str2double(TCMlist(i).ParamVar{1,2}));
   ideal_root_watts=fin_wall_htc*fin_areas(which_fin_length,which_N_fins)*(root_temps{i}-T_ambient);
   % ideal is Qdot = h*A*(T_root_average-T_fluid)
   fin_eff{i}=sum_root_watts./ideal_root_watts; %finally
end

figure(11)
[min_demo_eff,min_fin]=min(fin_eff{demo_result});  %keep in mind these should also mirror across the yz plane
[max_demo_eff,max_fin]=max(fin_eff{demo_result});
Temp_text=['S.S. Temp. Min eff is ',num2str(min_demo_eff),' at fin ',...
    num2str(min_fin),'. Max eff is ',num2str(max_demo_eff),' at fin ',num2str(max_fin),'.'];
Visualize(Temp_text,MIcell{demo_result},'State',Results{demo_result});  %plot temperature

