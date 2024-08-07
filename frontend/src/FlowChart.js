import React, { useCallback, useState } from 'react';
import {ReactFlow, addEdge, applyEdgeChanges, applyNodeChanges, Controls, Background, MiniMap,MarkerType } from '@xyflow/react';
import ButtonPanel from './ButtonPanel';
import NodePopup from './NodePopup';
// import ContextMenu from './ContextMenu';
import CustomNode from './CustomNode';
import FloatingEdge from './FloatingEdge';
import '@xyflow/react/dist/style.css';

// const nodeTypes = {
//   imageNode: ImageNode, // Register the ImageNode component
// };

const nodeTypes = {
  custom: CustomNode,
};
const FlowChart = ({ nodes, setNodes, setEdges, edges, updateNodeDetails }) => {
  // State for managing popup visibility and selected node
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  // const [label, setLabel] = useState('');
  // const [menu, setMenu] = useState(null);
  // const ref = useRef(null);
  const onEdgesChange = useCallback(
    (changes) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
      console.log('edges1', edges);
      ButtonPanel({ edges: edges });
    },
    [setEdges]
  );

  const onNodesChange = useCallback(
    (changes) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    console.log('nodes', nodes),
    []
  );

  const onConnect = useCallback(
    (connection) => {
      setEdges((eds) => addEdge(connection, eds));
      console.log('edges2', edges);
      ButtonPanel({ edges: edges });
    },
    [setEdges]
  );
  // const onNodeContextMenu = useCallback(
  //   (event, node) => {
  //     // Prevent native context menu from showing
  //     event.preventDefault();

  //     // Calculate position of the context menu. We want to make sure it
  //     // doesn't get positioned off-screen.
  //     const pane = ref.current.getBoundingClientRect();
  //     setMenu({
  //       id: node.id,
  //       top: event.clientY < pane.height - 200000&& event.clientY,
  //       left: event.clientX < pane.width - 2000 && event.clientX,
  //       right: event.clientX >= pane.width - 2000 && pane.width - event.clientX,
  //       bottom:
  //         event.clientY >= pane.height - 2000 && pane.height - event.clientY,
  //     });
  //   },
  //   [setMenu],
  // );
  // Handler for node double clicks
  const onNodeDoubleClick = (event, node) => {
    setIsPopupVisible(true);
  };
  // Handler for node clicks
  const onNodeClick = (event, node) => {
    setSelectedNode(node);
    // setLabel(node.data.label);
  };
  // const updateNodeName = (id, name) => {
  //   setNodes((nds) =>
  //     nds.map((node) => (node.id === id ? { ...node, data: { ...node.data, label: name } } : node))
  //   );
  // };

  // const handleLabelChange = (event) => {
  //   setLabel(event.target.value);
  //   updateNodeName(selectedNode.id, event.target.value);
  // };
  // const onPaneClick = useCallback(() => setMenu(null), [setMenu]);
  const defaultEdgeOptions = {
    style: { strokeWidth: 3, stroke: 'black' },
    type: 'floating',
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: 'black',
    },
  };
  const connectionLineStyle = {
    strokeWidth: 3,
    stroke: 'black',
  };
  // const nodeTypes = {
  //   custom: CustomNode,
  // };
  
  const edgeTypes = {
    floating: FloatingEdge,
  };

  return (
    <div className='flow-chart' style={{ position: 'relative' }}>
      <ReactFlow
        //  ref={ref}
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDoubleClick={onNodeDoubleClick} // Add the onNodeDoubleClick handler here
        onNodeClick={onNodeClick} // Add the onNodeClick handler here
        fitView
        onConnect={onConnect}
        // nodeTypes={nodeTypes} // Pass the nodeTypes object
        // onPaneClick={onPaneClick}
        // onNodeContextMenu={onNodeContextMenu}
        defaultEdgeOptions={defaultEdgeOptions}
        connectionLineStyle={connectionLineStyle}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        minZoom={0.01}
      >
        <Controls />
        <Background />
        <MiniMap pannable zoomable/>
        {/* {menu && <ContextMenu onClick={onPaneClick} {...menu} />} */}

      </ReactFlow>
      {/* <div className="updatenode__controls" style={{ position: 'absolute', top: '10px', left: '10px', backgroundColor: 'white', padding: '10px', zIndex: 1000 }}>
        <label>Name:</label>
        <input
          value={label}
          onChange={handleLabelChange}
        />
      </div> */}
      {isPopupVisible && <NodePopup node={selectedNode} onClose={() => setIsPopupVisible(false)} updateNodeDetails={updateNodeDetails} />}
    </div>
  );
};

export default FlowChart;
