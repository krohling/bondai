// ui/components/agent-button-panel.tsx
import { useState } from 'react';

interface ButtonProps {
  messageTool: string;
  escapedString: string;
  messageTooltip: {
    filename: string;
  };
}
  
const ButtonPanel = ({messageTool, escapedString, messageTooltip}: ButtonProps) => {

  const [isTooltipVisible, setTooltipVisibility] = useState(false);

  const handleDownload = (fileName: string) => {
    const url = `/api/download?fileName=${encodeURIComponent(fileName)}`;
    window.open(url, '_blank');
  };

  const toggleTooltip = () => {
    setTooltipVisibility(!isTooltipVisible);
  };

  return (
    <>
      <div className='pt-3 flex justify-end items-end'>
        {messageTooltip?.filename &&
        <button 
          onClick={() => handleDownload(messageTooltip?.filename)} 
          className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20"
        >
          Download File
        </button>
        }
        <button 
          className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20"
          onClick={toggleTooltip}>
          {messageTool}
          <span className="toggleSymbol"> {isTooltipVisible ? '-' : '+'}</span>
        </button>
      </div>
      <div className={`${isTooltipVisible ? '' : 'hidden'} w-full tooltip mt-2 p-3 w-100 bg-black/50 text-white rounded z-20`}>
        <pre className="whitespace-pre-wrap">
          {escapedString}
        </pre>
      </div>
    </>
  )
};

export default ButtonPanel