import React, { useState, useEffect } from 'react';
import MTBFModelPopup from './MTBFModelPopup';
import ValveMTBFModelPopup from './ValveMTBFModelPopup';

const NodePopup = ({ node, onClose, updateNodeDetails }) => {
  const [reliability, setReliability] = useState(0.9);
  const [mtbf, setMtbf] = useState(1);
  const [mttr, setMttr] = useState(0);
  const [showMTBFModelPopup, setShowMTBFModelPopup] = useState(false);
  const [pumpMTBFData, setPumpMTBFData] = useState({});
  const [pipeVibration, setPipeVibration] = useState(''); // State for dropdown selection
  const [valveMTBFData, setValveMTBFModelData] = useState({});
  const [warning, setWarning] = useState('');// State for warning message
  // const [time, setTime] = useState('100'); // Default time set to 100 hours
  // const [timeUnit, setTimeUnit] = useState('hours'); // State for time unit
  // const [reliability, setReliability] = useState(''); // State for calculated reliability
  const [availability, setAvailability] = useState(''); // State for calculated availability
  const [showValveMTBFModelPopup, setShowValveMTBFModelPopup] = useState(false);
  // Load saved values from localStorage when the component mounts
  useEffect(() => {
    const savedData = JSON.parse(localStorage.getItem(node.id));
    if (savedData) {
      setReliability(savedData.reliability);
      setMtbf(savedData.mtbf);
      setMttr(savedData.mttr);
      // setTime(savedData.time || '100'); // Default to 100 if not saved
      // setTimeUnit(savedData.timeUnit || 'hours');
      if (savedData.pipeVibration) {
        setPipeVibration(savedData.pipeVibration);
        updateMTBF(savedData.pipeVibration); // Update MTBF based on saved vibration state
      }
    }
  }, [node.id]);

  // useEffect(() => {
  //   if (time && mtbf) {
  //     calculateReliability();
  //   }
  // }, [time, mtbf, timeUnit]);

  useEffect(() => {
    calculateAvailability();
  }, [mtbf, mttr]);

  const handleMTBFModelClick = (e) => {
    e.preventDefault();
    setShowMTBFModelPopup(true);
  };

  const handleValveMTBFModelClick = (e) => {
    e.preventDefault();
    setShowValveMTBFModelPopup(true);
  };
  const pumpMTBFModeldata = (id, details) => {
    const updatedPumpMTBFData = {
      ...pumpMTBFData,
      [id]: details,
    };
    fetch('http://127.0.0.1:5000/api/pumpmtbfdata', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedPumpMTBFData),
    })
    .then(response => response.json())
    .then(data => {
      setPumpMTBFData(updatedPumpMTBFData);
      console.log('MTBF data updated:',data );
      setMtbf(data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  const valveMTBFModelData = (id, details) => {
    const updatedValveMTBFData = {
      ...valveMTBFData,
      [id]: details,
    };
    fetch('http://127.0.0.1:5000/api/valvemtbfdata', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedValveMTBFData),
    })
    .then(response => response.json())
    .then(data => {
      setValveMTBFModelData(updatedValveMTBFData);
      console.log('MTBF data updated:',data );
      setMtbf(data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  const updateMTBF = (vibration) => {
    const mtbf1 = 1 / ((0.47 / (10 ** 6)) * 1);
    const mtbf2 = 1 / ((0.47 / (10 ** 6)) * 1.2);
    // Update MTBF based on the vibration condition
    if (vibration === '1') {
      setMtbf(mtbf2); // Example value for pipe with vibrations
    } else if (vibration === '2') {
      setMtbf(mtbf1); // Example value for pipe with no vibrations
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const updatedData = {
      reliability: parseFloat(reliability),
      mtbf: parseFloat(mtbf),
      mttr: parseFloat(mttr),
      // time, timeUnit, and pipeVibration are not included in the data sent to the backend
    };
    updateNodeDetails(node.id, updatedData);

    // Save all data including time, timeUnit, and pipeVibration to localStorage
    const localStorageData = {
      ...updatedData,
      // time: time,
      // timeUnit: timeUnit,
      pipeVibration: pipeVibration,
    };
    localStorage.setItem(node.id, JSON.stringify(localStorageData));
    onClose();
  };

  const handleNumberChange = (setter, min, max, setWarning) => (e) => {
    const value = e.target.value;
    if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
      const numericValue = parseFloat(value);
      if (numericValue >= min && numericValue <= max) {
        setWarning('');
        setter(value);
      } else if (value === '') {
        setWarning('');
        setter(value);
      } else {
        setWarning(`Value must be between ${min} and ${max}`);
      }
    }
  };

  // const handleTimeChange = (e) => {
  //   const value = e.target.value;
  //   if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
  //     setTime(value);
  //   }
  // };

  // const handleTimeUnitChange = (e) => {
  //   setTimeUnit(e.target.value);
  // };

  // const calculateReliability = () => {
  //   let timeInHours;
  //   switch (timeUnit) {
  //     case 'minutes':
  //       timeInHours = parseFloat(time) / 60;
  //       break;
  //     case 'days':
  //       timeInHours = parseFloat(time) * 24;
  //       break;
  //     case 'months':
  //       timeInHours = parseFloat(time) * 24 * 30;
  //       break;
  //     case 'years':
  //       timeInHours = parseFloat(time) * 24 * 365;
  //       break;
  //     default:
  //       timeInHours = parseFloat(time);
  //   }
  //   const reliabilityValue = Math.exp(-timeInHours / mtbf);
  //   setReliability(reliabilityValue.toFixed(20));
  // };

  const calculateAvailability = () => {
    const mttr1=parseFloat(mttr);
    const mtbf1=parseFloat(mtbf);
    console.log(mtbf1, mttr1);
    const availabilityValue = mtbf1 / (mtbf1 + mttr1);
    setAvailability(availabilityValue.toFixed(20));
  };
  const styles = {
    popup: {
      position: 'absolute',
      top: '20%',
      left: '40%',
      backgroundColor: 'white',
      padding: '20px',
      zIndex: 100,
      border: '1px solid #ccc',
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
    },
    form: {
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    },
    label: {
      display: 'flex',
      justifyContent: 'space-between',
      marginBottom: '10px',
      alignItems: 'center'
    },
    input: {
      flex: 1,
      marginLeft: '10px',
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px'
    },
    dropdown: {
      flex: 1,
      marginLeft: '10px',
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px'
    },
    button: {
      marginTop: '10px',
      padding: '8px 16px',
      border: 'none',
      borderRadius: '4px',
      backgroundColor: '#007bff',
      color: 'white',
      cursor: 'pointer'
    },
    closeButton: {
      marginTop: '10px',
      padding: '8px 16px',
      border: 'none',
      borderRadius: '4px',
      backgroundColor: '#6c757d',
      color: 'white',
      cursor: 'pointer'
    },
    warning: {
      color: 'red',
      fontSize: '12px',
      marginTop: '-10px',
      marginBottom: '10px'
    },
    // reliabilityBlock: {
    //   backgroundColor: '#f8f9fa',
    //   padding: '10px',
    //   borderRadius: '4px',
    //   border: '1px solid #ccc',
    //   textAlign: 'center',
    //   marginBottom: '10px',
    //   fontSize: '16px',
    //   color: '#333'
    // }
  };

  return (
    <div style={styles.popup}>
      <form onSubmit={handleSubmit} style={styles.form}>
      <h3>{node.id}</h3>
      <label style={styles.label}>
          Reliability:
          <input 
            type="text" 
            value={reliability} 
            onChange={handleNumberChange(setReliability, 0, 1, setWarning)} 
            style={styles.input}
          />
        </label>
        {warning && <div style={styles.warning}>{warning}</div>}

        <label style={styles.label}>
          MTBF:
          <input 
            type="text" 
            value={mtbf} 
            onChange={handleNumberChange(setMtbf, 0, Infinity, setWarning)} 
            style={styles.input}
          />
        </label>
        <label style={styles.label}>
          MTTR:
          <input 
            type="text" 
            value={mttr} 
            onChange={handleNumberChange(setMttr, 0, Infinity, setWarning)} 
            style={styles.input}
          />
        </label>
        {/* <label style={styles.label}>
          Time:
          <input 
            type="text" 
            value={time} 
            onChange={handleTimeChange} 
            style={styles.input}
          />
          <select value={timeUnit} onChange={handleTimeUnitChange} style={styles.dropdown}>
            <option value="hours">Hours</option>
            <option value="minutes">Minutes</option>
            <option value="days">Days</option>
            <option value="months">Months</option>
            <option value="years">Years</option>
          </select>
        </label>
        {warning && <div style={styles.warning}>{warning}</div>} */}
        {node.id.includes('Valve') && (
            <button onClick={handleValveMTBFModelClick} style={styles.button}>
              Valve MTBF Model
            </button>
        )}
        {node.id.includes('Pump') && (
          <button onClick={handleMTBFModelClick} style={styles.button}>
            Pump MTBF Model
          </button>
        )}
        {node.id.includes('Pipe') && (
          <label style={styles.label}>
            Pipe MTBF Model:
            <select 
              value={pipeVibration} 
              onChange={(e) => {
                setPipeVibration(e.target.value);
                updateMTBF(e.target.value); // Update MTBF based on dropdown selection
              }} 
              style={styles.dropdown}
            >
              <option value="" disabled>Select</option>
              <option value="1">Pipe with vibrations</option>
              <option value="2">Pipe with no vibrations</option>
            </select>
          </label>
        )}
        <div style={styles.reliabilityBlock}>
          {/* <p>Reliability: {reliability}</p> */}
          <p>Availability: {availability}</p>
        </div>
        <button type="submit" style={styles.button}>Submit</button>
        <button onClick={onClose} style={styles.closeButton}>Close</button>
      </form>
      {showMTBFModelPopup && <MTBFModelPopup nodeId={node.id} pumpMTBFModeldata={pumpMTBFModeldata} onClose={() => setShowMTBFModelPopup(false)} />}
      {showValveMTBFModelPopup && <ValveMTBFModelPopup nodeId={node.id} valveMTBFModelData={valveMTBFModelData} onClose={() => setShowValveMTBFModelPopup(false)} />}
    </div>
  );
};

export default NodePopup;