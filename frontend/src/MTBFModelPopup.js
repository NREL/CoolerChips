import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { createPortal } from 'react-dom';

const MTBFModelPopup = ({ nodeId, pumpMTBFModeldata, onClose }) => {
  const [bearingData, setBearingData] = useState({
    bearingType: 'Ball Bearing', Ls: '1000', La: '12', Vo: '12', Vl: '40', Cw: '0.005', T: '40', BearingDiameter: '5', Particle_size: '10'
  });
  const [fluidDriverData, setFluidDriverData] = useState({
    fluid_driver: '0.20', casings_options: 'Ordinary volute', Q: '50', Qr: '100', Vo: '25', Vd: '50', Fac: '10'
  });
  const [shaftData, setShaftData] = useState({ TAT: '100', TS: '70', shaftSurfaceOptions: 'Ground Shaft' });
  const [sealData, setSealData] = useState({
    Ps: '1500', Qf: '0.005', Dsl: '10', M: '20', C: '43', F: '32', V: '6.3', TR: '80', To: '40', C0: '10', Fr: '100'
  });

  const fluidDriverValues = {
    "Centrifugal, Axial flow impeller, Closed/open impellers": 0.20,
    "Centrifugal, Mixed flow/radial impeller, Open/semi-open/Closed impellers": 0.12,
    "Centrifugal, Peripheral, Single stage/multistage": 0.20,
    "Displacement, Reciprocating, Piston/plunger": 1.18,
    "Displacement, Reciprocating, Diaphragm": 0.58,
    "Displacement, Rotary (Single), Vane": 0.4,
    "Displacement, Rotary (Single), Piston": 1.05,
    "Displacement, Rotary (Multiple), Gear": 0.75,
    "Displacement, Rotary (Multiple), Lobe": 0.45,
    "Displacement, Rotary (Multiple), Screw": 0.58,
  };
  const casingOptions = [
    "Ordinary volute",
    "Modified volute",
    "Double volute",
    "Displacement pumps"
  ];

  const handleInputChange = (e, setData) => {
    const { name, value } = e.target;
    setData(prevState => ({ ...prevState, [name]: value }));
  };

  const handleFluidDriverChange = (e) => {
    const { value } = e.target;
    setFluidDriverData(prevState => ({
      ...prevState,
      fluid_driver_options: value,
      fluid_driver: fluidDriverValues[value] || ''
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    pumpMTBFModeldata(nodeId, { 
      bearingData: bearingData, 
      fluidData: fluidDriverData,
      shaftData: shaftData,
      sealData:sealData,
    });
    const localPumpdata = {
      bearingData:bearingData,
      fluidData:fluidDriverData,
      shaftData:shaftData,
      sealData:sealData,
    };
    localStorage.setItem(nodeId+"Pump", JSON.stringify(localPumpdata));
    onClose();

  };

  useEffect(() => {
    console.log('nodeId', nodeId);
    
    const savedData = JSON.parse(localStorage.getItem(nodeId+"Pump"));
    console.log('saved data',savedData);
    if (savedData) {
      setSealData(savedData.sealData);
      setShaftData(savedData.shaftData);
      setFluidDriverData(savedData.fluidData); // Default to 100 if not saved
      setBearingData(savedData.bearingData);
    }
  }, [nodeId]);



  const renderInput = (label, name, value, onChange, type = 'text') => (
    <div style={styles.inputContainer}>
      <label style={styles.label}>{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        style={styles.input}
        step="any" // Ensures that the input can accept floating-point numbers
      />
    </div>
  );

  const renderSelect = (label, name, value, options, onChange) => (
    <div style={styles.inputContainer}>
      <label style={styles.label}>{label}</label>
      <select name={name} value={value} onChange={onChange} style={styles.input}>
        <option value="" disabled>Select {label}</option>
        {options.map(option => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    </div>
  );

  return createPortal(
    <div style={styles.popup}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2>MTBF Model Data</h2>
        

        <h3>Bearing Data</h3>
        {renderSelect('Bearing Type', 'bearingType', bearingData.bearingType, ['Ball Bearing', 'Roller Bearing'], (e) => handleInputChange(e, setBearingData))}
        {renderInput('Dynamic Load Rating (Ls)', 'Ls', bearingData.Ls, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Equivalent Radial Load (La)', 'La', bearingData.La, (e) => handleInputChange(e, setBearingData), 'number')}
        {/* {renderInput('Reliability (R)', 'R', bearingData.R, (e) => handleInputChange(e, setBearingData), 'number')} */}
        {renderInput('Viscosity of Specification Lubricant (Vo)', 'Vo', bearingData.Vo, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Viscosity of Lubricant Used (Vl)', 'Vl', bearingData.Vl, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Percentage of Water in Lubricant (Cw)', 'Cw', bearingData.Cw, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Operating Temperature of a Bearing (T)', 'T', bearingData.T, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Bearing Diameter', 'BearingDiameter', bearingData.BearingDiameter, (e) => handleInputChange(e, setBearingData), 'number')}
        {renderInput('Particle Size', 'Particle_size', bearingData.Particle_size, (e) => handleInputChange(e, setBearingData), 'number')}


        <h3>Fluid Driver Data</h3>
        {renderSelect('Fluid Driver Options', 'fluid_driver_options', fluidDriverData.fluid_driver_options, [
          "Centrifugal, Axial flow impeller, Closed/open impellers",
          "Centrifugal, Mixed flow/radial impeller, Open/semi-open/Closed impellers",
          "Centrifugal, Peripheral, Single stage/multistage",
          "Displacement, Reciprocating, Piston/plunger",
          "Displacement, Reciprocating, Diaphragm",
          "Displacement, Rotary (Single), Vane",
          "Displacement, Rotary (Single), Piston",
          "Displacement, Rotary (Multiple), Gear",
          "Displacement, Rotary (Multiple), Lobe",
          "Displacement, Rotary (Multiple), Screw"
        ], handleFluidDriverChange)}
        {renderSelect('Casing Options', 'casings_options', fluidDriverData.casings_options, casingOptions, (e) => handleInputChange(e, setFluidDriverData))}
        {renderInput('Actual Operating Flow (Q)', 'Q', fluidDriverData.Q, (e) => handleInputChange(e, setFluidDriverData), 'number')}
        {renderInput('Maximum Pump Specified Flow (Qr)', 'Qr', fluidDriverData.Qr, (e) => handleInputChange(e, setFluidDriverData), 'number')}
        {renderInput('Operating Speed (Vo)', 'Vo', fluidDriverData.Vo, (e) => handleInputChange(e, setFluidDriverData), 'number')}
        {renderInput('Maximum Allowable Speed (Vd)', 'Vd', fluidDriverData.Vd, (e) => handleInputChange(e, setFluidDriverData), 'number')}
        {renderInput('Filter Size (Fac)', 'Fac', fluidDriverData.Fac, (e) => handleInputChange(e, setFluidDriverData), 'number')}
        {/* {renderInput('Cpf', 'Cpf', fluidDriverData.Cpf, (e) => handleInputChange(e, setFluidDriverData), 'number')} */}

        <h3>Shaft Data</h3>
        {renderSelect('Shaft Surface Options', 'shaftSurfaceOptions', shaftData.shaftSurfaceOptions, [
          "Ground Shaft", "Polished Shaft", "Hot Rolled Shaft"
        ], (e) => handleInputChange(e, setShaftData))}
        {renderInput('Operating Temperature (F) (TAT)', 'TAT', shaftData.TAT, (e) => handleInputChange(e, setShaftData), 'number')}
        {renderInput('Tensile Strength (kpsi) (TS)', 'TS', shaftData.TS, (e) => handleInputChange(e, setShaftData), 'number')}

        <h3>Seal Data</h3>
        {renderInput('Pressure at Seal (Ps)', 'Ps', sealData.Ps, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Allowable Leakage (Qf)', 'Qf', sealData.Qf, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Inner Diameter of Seal (Dsl)', 'Dsl', sealData.Dsl, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Meyer Hardness (lbs/in²) (M)', 'M', sealData.M, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Contact Pressure (lbs/in²) (C)', 'C', sealData.C, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Surface Finish (F)', 'F', sealData.F, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Dynamic Viscosity of Fluid (V)', 'V', sealData.V, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Rated Temperature of Seal (F) (TR)', 'TR', sealData.TR, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Operating Temperature of Seal (To)', 'To', sealData.To, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('System Filter Size in Microns (C0)', 'C0', sealData.C0, (e) => handleInputChange(e, setSealData), 'number')}
        {renderInput('Rated Flow Rate (GPM) (Fr)', 'Fr', sealData.Fr, (e) => handleInputChange(e, setSealData), 'number')}

        <button type="submit" style={styles.button}>Submit</button>
        <button type="button" onClick={onClose} style={styles.button}>Close</button>
      </form>
    </div>,
    document.body
  );
};

MTBFModelPopup.propTypes = {
  nodeId: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

const styles = {
  popup: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: 'white',
    padding: '20px',
    zIndex: 101,
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    width: '80%',
    maxHeight: '90vh',
    overflowY: 'auto',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  inputContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  label: {
    marginBottom: '5px',
    fontWeight: 'bold',
    fontSize: '14px',
    color: '#333',
  },
  input: {
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '14px',
  },
  button: {
    marginTop: '10px',
    padding: '10px 16px',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
    fontSize: '14px',
  },
  closeButton: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '20px',
    cursor: 'pointer',
  },
};

export default MTBFModelPopup;