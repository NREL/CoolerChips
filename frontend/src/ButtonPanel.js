// ButtonPanel.js
import React from 'react';
const ButtonPanel = ({ addNode, edges, nodeDetails }) => {
  const buttons = ['Junction', 'Pipe', 'Pump', 'Sink', 'External Grid', 'Heat Exchanger', 'Valve', 'Circulation Pump Mass']
  // ,'Source','Mass Storage','Circulation Pump Pressure','Compressor','Pressure Control','Flow Control'];
  const reliabilityButton = 'Reliability';
  const availabilityButton = 'Availability';

  const sendDatatoBackend = (dataToSend, edges, nodeDetails) => {
    fetch('http://127.0.0.1:5000/api/send-edges', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // Include edges and nodeDetails in the request body along with the calculation type
        body: JSON.stringify({
          calculationType: dataToSend,
          edges: edges,
          nodeDetails: nodeDetails
        }),
    })
    .then(response => response.json())
    .then(data => {
      const formattedData = Object.entries(data).map(([key, value]) => `${key}: ${value}`).join('\n');
      alert(formattedData);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  };
  const handleReliabilityClick = () => {
    console.log('Reliability button clicked');
    sendDatatoBackend("Reliability", edges, nodeDetails);
  };
  
  const handleAvailabilityClick = () => {
    console.log('Availability button clicked');
    sendDatatoBackend("Availability", edges, nodeDetails);
  };

  return (
    <div className="button-panel">
      {buttons.map((label) => (
        <button key={label} onClick={() => addNode(label)}>
          {label}
        </button>
      ))}
      <button onClick={handleReliabilityClick}>{reliabilityButton}</button>
      <button onClick={handleAvailabilityClick}>{availabilityButton}</button>
    </div>
  );
};

export default ButtonPanel;