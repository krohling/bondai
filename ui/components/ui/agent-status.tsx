import React from 'react';

interface AgentStatusProps {
  status?: string;
}

const AgentStatus: React.FC<AgentStatusProps> = ({ status }) => {
  
  if (status === 'inactive') {
    return (
      <>
        <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-slate-500 bg-transparent ml-2"></span>
      </>
    );
  } else if (status === 'active') {
    return (
      <>
        <span className="relative flex h-3 w-3 ml-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </span>
      </>
    );
  } else {
    return (
      <>
        <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-white-500 bg-transparent mr-2"></span>
      </>
    );
  }

};

export default AgentStatus;