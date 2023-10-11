// app/test/page.tsx 
"use client"
import React, { useState } from 'react';

export default function YourComponent() {
    const [isTooltipVisible, setTooltipVisibility] = useState(false);
  
    const toggleTooltip = () => {
      setTooltipVisibility(!isTooltipVisible);
    };
    
    const convertObjectToString = (obj: any): string => {
      let str = '';
      for (const [key, value] of Object.entries(obj)) {
        if (typeof value === 'object' && value !== null) {
          str += `${key.charAt(0).toUpperCase() + key.slice(1)}: \n${convertObjectToString(value)}\n`;
        } else {
          str += `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}\n`;
        }
      }
      return str.trim();
    };

    const json = `
    {
      "data": {
        "step": {
          "error": "false",
          "exit": "false",
          "function": {
            "arguments": {
              "append": false,
              "filename": "test.txt",
              "text": "test",
              "thought": "Using the file_write tool to write the word 'test' into a file named 'test.txt'. If the file already exists, it will be overwritten."
            },
            "name": "file_write"
          },
          "message": "# Next Steps #\\n\\nThe task is straightforward and can be completed in a single step using the 'file_write' tool. We need to write the word 'test' into a file named 'test.txt'. The parameters for the 'file_write' tool should be set as follows:\\n\\n- 'filename': 'test.txt'\\n- 'text': 'test'\\n- 'append': false\\n\\nThis will ensure that the word 'test' is written into the file 'test.txt', and if the file already exists, it will be overwritten. \\n\\nLet's proceed with this step.",
          "output": "File test.txt written successfully"
        }
      },
      "event": "agent_step_completed"
    }
    `;

    let escapedString;
    let object = JSON.parse(json);
    console.log('object', object);
    
    escapedString = convertObjectToString(object.data.step.function.arguments);
    console.log('escapedString 1:', escapedString);

    escapedString = encodeURIComponent(JSON.stringify(json) || '');
    console.log('escapedString 2', escapedString);
      
    return (
      <></>
    )




























    return (
      <div className="p-20  h-screen">
        <button 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700 focus:outline-none relative z-10"
            onClick={toggleTooltip}>
            Toggle Tooltip
        </button>
          {isTooltipVisible && 
            <div className="tooltip absolute mt-2 p-3 w-100 bg-black/50 text-white rounded z-20">
                <pre className="whitespace-pre-wrap">{`import getpass

# Function to play the hangman game
def play_hangman():
    # Player 1 enters the word
    word = getpass.getpass('Enter the word for the game: ')
    
    # The guess box is obscured by asterisks
    guessed_word = ['*' for _ in word]
    print('The word has', len(word), 'letters')
    
    # Player 2 guesses the letters
    while '*' in guessed_word:
        guess = input('Guess a letter: ')
        
        # Check if the guessed letter is in the word
        for i in range(len(word)):
            if word[i] == guess:
                guessed_word[i] = guess
        
        print(''.join(guessed_word))
    
    print('Congratulations, you guessed the word!')

# Start the game
play_hangman()`}
                </pre>
            </div> 
          }
      </div>
    );
  }
