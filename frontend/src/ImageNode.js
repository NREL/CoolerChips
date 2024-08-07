import React, { memo } from "react";
import { Handle, Position } from "react-flow-renderer";

export default memo(({ data, isConnectable }) => {
  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        onConnect={(params) => console.log("handle onConnect", params)}
        isConnectable={isConnectable}
      />
      <div style={{ textAlign: 'center' }}> {/* Center the label and image */}
        {data.label && <div>{data.label}</div>} {/* Conditionally render the label if it exists */}
        <img src={data.image.url} alt={data.image.alt} />
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </>
  );
});