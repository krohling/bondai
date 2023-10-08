// /app/test/test.client.tsx
import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';

const SimpleChat = () => {
  const [messages, setMessages] = useState<string[]>(['Ready..']);
  const [ws, setWs] = useState<WebSocket | null>(null);
  // let socket: Socket;

  useEffect(() => {
    const socket = io('ws://localhost:2663', {
      transports: [ 'websocket' ],
      upgrade: false
    });

    socket.on('agent_started', () => {
      console.log('Agent has started.');
    });

    socket.on('agent_completed', () => {
      console.log('Agent has completed.');
    });

    socket.on('agent_step_completed', (data) => {
      console.log('Agent step completed with data:', data);
    });

    socket.on('connect', () => {
      console.log('Successfully connected to the server.');
    });

    socket.on('disconnect', () => {
      console.log('websocket disconnected.');
    });

    socket.on('message', (data) => {
      console.log('Message received:', data);
    });

    socket.on('connect_error', (error) => {
      console.log('Connection Error:', error);
    });

    socket.on('reconnect', (attempt) => {
      console.log('WebSocket reconnected. Attempt:', attempt);
    });

    socket.on('reconnect_attempt', (attempt) => {
      console.log('Attempting to reconnect. Attempt:', attempt);
    });

    socket.on('reconnect_failed', () => {
      console.log('Reconnection Failed');
    });
    
    socket.on('reconnect_error', (error) => {
      console.log('Reconnection Error:', error);
    });

    socket.on('agent_message', (msg) => {
      console.log('Received:', msg);
    });

    setWs(socket);

    fetch('http://localhost:2663/agent/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ })
    })

    return () => {
      socket.disconnect();
    };
    
  }, []);

  const sendMessageToAgent = (message: string) => {
    console.log('sendMessageToAgent: sending..', ws);
    if (ws) {
      ws.emit('message', {
        'event': 'user_message',
        'data': { message }
      } );
    }
  };

  return (
    <div className='m-5'>
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
      <button className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 my-3 rounded' onClick={() => sendMessageToAgent('write the word test and save it to file. no budget and no other criteria. please proceed. accept this as confirmation to go ahead without asking permission again.')}>Send Message</button>
    </div>
  );
};

export default SimpleChat;