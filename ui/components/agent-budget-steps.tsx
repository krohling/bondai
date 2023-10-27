// ui/components/agent-budget-steps.tsx
import React, { useState, useEffect, ChangeEvent } from 'react';
import { toast } from 'react-hot-toast';


export const AgentBudgetSteps = () => {
  const [budgetValue, setBudgetValue] = useState<string>('0.00');
  const [maxStepsValue, setMaxStepsValue] = useState<string>('10');

  const setBudget = () => {
    localStorage.setItem('budget', budgetValue);
    toast.success('Budget set!');
  };

  const setMaxSteps = () => {
    localStorage.setItem('maxSteps', maxStepsValue);
    toast.success('Max Steps set!');
  };

  const handleBudgetChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    setBudgetValue(e.target.value);
  };

  const handleMaxStepsChange = (e: ChangeEvent<HTMLInputElement>) => {
    setMaxStepsValue(e.target.value);
  };

  useEffect(() => {
    const init = async () => {
      setBudgetValue(localStorage.getItem('budget') || '0.00');
      setMaxStepsValue(localStorage.getItem('maxSteps') || '10');
    }
    init();
  }, []);

  return (
    <>
      <div className='flex items-center mb-5'>
        <div className='relative text-gray-400 focus-within:text-gray-600x'>
          <div className='text-sm text-black dark:text-white py-1.5 pointer-events-none w-8 h-8 absolute top-1/2 transform -translate-y-1/2 left-3'>$</div>
          <input 
            type='number' 
            className='w-[110px] bg-black/70 mr-2 pl-6 pr-4 py-1.5 shadow-sm dark:shadow-lg rounded border text-black dark:text-white text-sm'
            value={budgetValue} 
            onChange={handleBudgetChange} />
        </div>
        <button 
          className='w-auto bg-black/70 border hover:bg-white/20 shadow-sm dark:shadow-lg text-xs py-2 px-3 mr-2 rounded text-black dark:text-white whitespace-nowrap'
          onClick={() => setBudget()}>
          Set Max Budget
        </button>
      </div>

      <div className='flex items-center'>
        <input 
          type='number' 
          className='w-[110px] bg-black/70 mr-2 px-2.5 py-1.5 shadow-sm dark:shadow-lg border rounded text-black dark:text-white text-sm'
          value={maxStepsValue} 
          onChange={handleMaxStepsChange} />
        <button 
          className='w-auto bg-black/70 border hover:bg-white/20 shadow-sm dark:shadow-lg text-xs py-2 px-3 rounded text-black dark:text-white whitespace-nowrap'
          onClick={() => setMaxSteps()}>
          Set Max Steps
        </button>
      </div>

    </>
  )
};