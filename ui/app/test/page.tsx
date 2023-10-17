// app/test/page.tsx
"use client"
import SimpleChat from './test.client';

export default function TestPage() {

  return (
    <div className='m-5'>
      <h1>BondAi Agent</h1>
      <SimpleChat />
    </div>
  );
};