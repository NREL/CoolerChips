// FlowChart.js
  // Import useState to manage state for the popup visibility and the selected node
import React, { useCallback, useState } from 'react';
import ReactFlow, { addEdge, applyEdgeChanges, applyNodeChanges, Controls, Background, MiniMap } from 'react-flow-renderer';
import ButtonPanel from './ButtonPanel';
import NodePopup from './NodePopup';

const FlowChart = ({ nodes, setNodes, setEdges, edges, updateNodeDetails }) => {

  // State for managing popup visibility and selected node
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  const onEdgesChange = useCallback(
    (changes) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
      console.log('edges1', edges);
      ButtonPanel({edges:edges});    
    },
    [setEdges]
  );

  const onNodesChange = useCallback(
      (changes) => {
        setNodes((nds) => applyNodeChanges(changes, nds));
      },
      []
    );

  const onConnect = useCallback(
    (connection) =>{ 
      setEdges((eds) => addEdge(connection, eds));
      console.log('edges2', edges);
      ButtonPanel({edges:edges});    
    },
    [setEdges]
    
  );

  // Handler for node double clicks
  const onNodeDoubleClick = (event, node) => {
    setSelectedNode(node);
    setIsPopupVisible(true);
  };

  return (
    <div className='flow-chart'>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDoubleClick={onNodeDoubleClick} // Add the onNodeDoubleClick handler here
      >
        <Controls />
        <Background />
        <MiniMap />
      </ReactFlow>
      {isPopupVisible && <NodePopup node={selectedNode} onClose={() => setIsPopupVisible(false)} updateNodeDetails={updateNodeDetails} />}
    </div>
  );
};

export default FlowChart;