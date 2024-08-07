import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { createPortal } from 'react-dom';

const ValveMTBFModelPopup = ({ nodeId, valveMTBFModelData, onClose }) => {
  const [valveData, setValveData] = useState({
    Nc:'1.0',
    dP:'1.0',
    Qf:'1.0',
    mu:'1.0',
    B:'1.0',
    DS:'1.0',
    nu:'1.0',
    Fr_actual:'1.0',
    Fr_rated:'1.0',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setValveData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    valveMTBFModelData(nodeId, valveData);
    localStorage.setItem(nodeId + "Valve", JSON.stringify(valveData));
    onClose();
  };

  useEffect(() => {
    const savedData = JSON.parse(localStorage.getItem(nodeId + "Valve"));
    if (savedData) {
      setValveData(savedData);
    }
  }, [nodeId]);

  const renderInput = (label, name, value, onChange, type = 'text') => (
    <div className="form-group">
      <label htmlFor={name}>{label}</label>
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        className="form-control"
      />
    </div>
  );

  return createPortal(
    <div style={styles.popup}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2>Valve Model Data</h2>
          {renderInput('Average time to complete a cycle of operation in hours ', 'Nc', valveData.Nc, handleInputChange)}
          {renderInput('Pressure Drop across Valve in psi ', 'dP', valveData.dP, handleInputChange)}
          {renderInput('Allowable leakage rate in^3/min ', 'Qf', valveData.Qf, handleInputChange)}
          {renderInput('Dynamic fluid viscosity in lbf-min/in^2 ', 'mu', valveData.mu, handleInputChange)}
          {renderInput('Spool clearance in micrometer ', 'B', valveData.B, handleInputChange)}
          {renderInput('Spool diameter in inches ', 'DS', valveData.DS, handleInputChange)}
          {renderInput('Friction coefficient ', 'nu', valveData.nu, handleInputChange)}
          {renderInput('Actual Flow rate through the valve ', 'Fr_actual', valveData.Fr_actual, handleInputChange)}
          {renderInput('Rated Flow rate through the valve ', 'Fr_rated', valveData.Fr_rated, handleInputChange)}

          <button type="submit" style={styles.button}>Submit</button>
          <button type="button" onClick={onClose} style={styles.button}>Close</button>
      </form>
    </div>,
    document.body
  );
};

ValveMTBFModelPopup.propTypes = {
  nodeId: PropTypes.string.isRequired,
  valveMTBFModelData: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired
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

export default ValveMTBFModelPopup;
