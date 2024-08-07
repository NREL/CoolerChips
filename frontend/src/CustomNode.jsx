import { Handle, Position, useConnection } from '@xyflow/react';

export default function CustomNode({ data }) {
  const connection = useConnection();
  const isConnecting = !!connection.startHandle;
  const isTarget = connection.startHandle && connection.startHandle.nodeId !== data.label;

  // const label = isTarget ? 'Drop here' : data.label;

  return (
    <div className="customNode">
      <div
        className="customNodeBody"
        style={{
          borderStyle: isTarget ? 'dashed' : 'solid',
          backgroundColor: 'white',
        }}
      >
        {/* If handles are conditionally rendered and not present initially, you need to update the node internals https://reactflow.dev/docs/api/hooks/use-update-node-internals/ */}
        {/* In this case we don't need to use useUpdateNodeInternals, since !isConnecting is true at the beginning and all handles are rendered initially. */}
        {!isConnecting && (
          <Handle
            className="customHandle"
            position={Position.Right}
            type="source"
          />
        )}
      <div style={{ textAlign: 'center',}}> {/* Center the label and image */}
        {data.label && <div>{data.label}</div>}
        <img src={data.image.url} alt={data.image.alt} />
      </div>
        <Handle
          className="customHandle"
          position={Position.Left}
          type="target"
          isConnectableStart={false}
        />
        {/* {label} */}
      </div>
    </div>
  );
}
