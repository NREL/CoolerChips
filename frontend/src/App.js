// App.js
import React, { useEffect, useState } from 'react';
import ButtonPanel from './ButtonPanel';
import FlowChart from './FlowChart';
import './App.css';

function App() {
  const [nodes, setNodes] = useState([]);
  const [nodeCounts, setNodeCounts] = useState({});
  const [edges, setEdges] = useState([]);
  const [nodeDetails, setNodeDetails] = useState({}); // New state for node details

  const addNode = (label) => {
    setNodes((nds) => {
      const count = nodeCounts[label] ? nodeCounts[label] + 1 : 1;
      const newNode = {
        id: `${label} ${count}`,
        data: { label: `${label} ${count}`, index: nds.length + 1 },
        position: { x: Math.random() * 500, y: Math.random() * 500 },
      };
      return [...nds, newNode];
    });
    setNodeCounts((prevCounts) => ({
      ...prevCounts,
      [label]: (prevCounts[label] || 0) + 1,
    }));
  };

    // New function to update node details
  const updateNodeDetails = (id, details) => {
    setNodeDetails((prevDetails) => ({
      ...prevDetails,
      [id]: details,
    }));
  };
  console.log("nodeDetails",nodeDetails);
  useEffect(() => {}, [nodes]);

  console.log(nodes);

  return (
    <div className="App">
      <header className="App-header">
        <h1>MOSTCOOL Reliability</h1>  
      </header>
      <div className="App-body">
      <ButtonPanel addNode={addNode} edges={edges} nodeDetails={nodeDetails} />
        <FlowChart nodes={nodes} setNodes={setNodes} setEdges={setEdges} edges={edges} updateNodeDetails={updateNodeDetails} />
      </div>  
    </div>
  );
}

export default App;