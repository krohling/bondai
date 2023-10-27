// ui/components/agent-settings.tsx
import React, { useState, useEffect, ChangeEvent } from 'react';
import { toast } from 'react-hot-toast';


export const AgentSettings = () => {
  const placeholder: string = '';

  const placeholderChange = () => {
  };
  const setChange = () => {
  };

  return (
    <div className='flex flex-col sm:flex-row justify-between items-center mt-10 space-y-5 sm:space-y-0 sm:space-x-5'>

      <div className='mb-4'>
        <input 
          type='text' 
          className=' bg-black/70 mr-2 p-2.5 shadow-sm dark:shadow-lg border rounded text-black dark:text-white text-xs'
          placeholder='Bot Name' 
          onChange={placeholderChange} />

      </div>
      
    </div>
  )
};