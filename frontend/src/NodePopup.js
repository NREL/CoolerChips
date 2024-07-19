// NodePopup.js
import React, { useState } from 'react';

const NodePopup = ({ node, onClose, updateNodeDetails }) => {
    const [reliability, setReliability] = useState('');
    const [mtbf, setMtbf] = useState('');
    const [mttr, setMttr] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    updateNodeDetails(node.id, { reliability: parseFloat(reliability), mtbf: parseFloat(mtbf), mttr: parseFloat(mttr) });
    onClose(); // Close the popup after submitting
  };
  
  // Updated styles for cleaner UI
  const popupStyle = {
    position: 'absolute',
    top: '20%',
    left: '40%',
    backgroundColor: 'white',
    padding: '20px',
    zIndex: 100,
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
  };

  const formStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  };
  const labelStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
    alignItems: 'center'
  };
  const buttonStyle = {
    marginTop: '10px',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer'
  };
  const inputStyle = {
    flex: '1',
    marginLeft: '10px',
    padding: '8px',
    border: '1px solid #ccc',
    borderRadius: '4px'
  };
  const closeButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#6c757d'
  };

  return (
    <div style={popupStyle}>
      <form onSubmit={handleSubmit} style={formStyle}>
        <h3>{node.id}</h3>
        <label style={labelStyle}>
        Reliability:
            <input type="number" step="0.000001" min="0" max="1" value={reliability} onChange={(e) => setReliability(e.target.value)} style={inputStyle}/>
        </label>
        <label style={labelStyle}>
        MTBF:
          <input type="number" step="0.01" min="0" value={mtbf} onChange={(e) => setMtbf(e.target.value)}style={inputStyle} />
        </label>
        <label style={labelStyle}>
        MTTR:
          <input type="number" step="0.01" min="0" value={mttr} onChange={(e) => setMttr(e.target.value)} style={inputStyle}/>
        </label>
        <button type="submit" style={buttonStyle}>Submit</button>
        <button onClick={onClose} style={closeButtonStyle}>Close</button>
      </form>
    </div>
  );
};

export default NodePopup;