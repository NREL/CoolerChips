// ButtonPanel.js
import React  from 'react';
import imageMap from './App';
import * as XLSX from 'xlsx';

function ButtonPanel({ addNode, edges, nodeDetails, setNodes, setEdges,nodes ,setNodeDetails}) {
  const buttons = ['Junction', 'Pipe', 'Pump', 'Sink', 'External Grid', 'Heat Exchanger', 'Valve', 'Circulation Pump Mass']
  // ,'Source','Mass Storage','Circulation Pump Pressure','Compressor','Pressure Control','Flow Control'];
  const reliabilityButton = 'Reliability';
  const availabilityButton = 'Availability';
  const costDataButton = 'Cost Data';
  
  const uploadButton = 'Upload Excel';

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
    console.log(edges);
    console.log(nodeDetails);
    sendDatatoBackend("Reliability", edges, nodeDetails);
  };
  
  const handleAvailabilityClick = () => {
    console.log('Availability button clicked');
    sendDatatoBackend("Availability", edges, nodeDetails);
  };

  const sendDatatoCost = (nodes) => {
    fetch('http://127.0.0.1:5000/api/cost-data', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nodes: nodes,
        nodeDetails: nodeDetails
      }),
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'rbd_label.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    // .then(response => response.json())
    // .then(data => {
    //   // const formattedData = Object.entries(data).map(([key, value]) => `${key}: ${value}`).join('\n');
    //   // alert(formattedData);
    //   alert(data);
    // })
    .catch((error) => {
        console.error('Error:', error);
    });
  }

  const handleCostClick =() =>{
    console.log('Cost Data button clicked');
    console.log(nodes);
    sendDatatoCost(nodes);
  };
  const createDefaultLayout = () => {
    setNodes((currentNodes) => {
      const nextIndex = currentNodes.length + 1;
      const image = imageMap['Junction'] || {url:"data:image/png;base64,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"};
      const junction1 = {
        id: `Junction ${nextIndex}`,
        type: 'custom', // Specify the custom node type
        data: { 
          label: `Junction ${nextIndex}`, 
          index: nextIndex,
          image: image
        },
        position: { x: Math.random() * 500, y: Math.random() * 500 },
      };

      const pipe = {
        id: `Pipe ${nextIndex}`,
        type: 'custom', // Specify the custom node type
        data: { 
          label: `Pipe ${nextIndex}`, 
          index: nextIndex,
          image: image
        },
        position: { x: Math.random() * 500, y: Math.random() * 500 },
      };
      const junction2 = {
        id: `Junction ${nextIndex+1}`,
        type: 'custom', // Specify the custom node type
        data: { 
          label: `Junction ${nextIndex+1}`, 
          index: nextIndex,
          image: image
        },
        position: { x: Math.random() * 500, y: Math.random() * 500 },
      };

      const edge1 = { id: `e${nextIndex}-${nextIndex + 1}`, source: junction1.id, target: pipe.id };
      const edge2 = { id: `e${nextIndex + 1}-${nextIndex + 2}`, source: pipe.id, target: junction2.id };

      setEdges((currentEdges) => [...currentEdges, edge1, edge2]);

      return [...currentNodes, junction1, pipe, junction2];
    });
  };

  const saveToExcel = () => {
      if (typeof nodeDetails !== 'object' || Array.isArray(nodeDetails)) {
        console.error('nodeDetails is not a valid object');
        return;
      }
    
      const nodeDetailsArray = Object.keys(nodeDetails).map(key => ({
        name: key,
        ...nodeDetails[key]
      }));
    
      const ws = XLSX.utils.json_to_sheet(nodeDetailsArray);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'NodeDetails');
      XLSX.writeFile(wb, 'node_details.xlsx');
    };

    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      const reader = new FileReader();
    
      reader.onload = (e) => {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);
    
        // Transform the data structure
        const transformedData = jsonData.reduce((acc, item) => {
          const { name, ...details } = item;
          acc[name] = details;
          return acc;
        }, {});
    
        setNodeDetails(transformedData);
        console.log("Node details updated from Excel file:", transformedData);
      };
    
      reader.readAsArrayBuffer(file);
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
      <button onClick={handleCostClick}>{costDataButton}</button>
      <button onClick={createDefaultLayout}>Default Layout</button>
      <button onClick={saveToExcel}>Save</button>
      <input
        type="file"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
        accept=".xlsx, .xls"
        id="fileUploadInput"
      />
      <button onClick={() => document.getElementById('fileUploadInput').click()}>{uploadButton}</button>
      </div>
  );
};

export default ButtonPanel;