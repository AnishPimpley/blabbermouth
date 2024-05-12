'use client';

import { useCallback, useEffect, useState } from 'react';
import { Tldraw } from 'tldraw';
import './index.css';
import { FloatButton } from 'antd';
import { AudioOutlined } from '@ant-design/icons';
const Groq = require("groq-sdk");
const groq = new Groq({apiKey: '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', dangerouslyAllowBrowser: true});

// import openai from 'openai';
import OpenAI from 'openai';
import test from 'node:test';

interface CircleProps {
  radius: number;
}

const Circle: React.FC<CircleProps> = ({ radius }) => {
  return (
    <div style={{ width: '100px', height: '100px', borderRadius: '50%', backgroundColor: 'blue' }}>
      Circle with radius {radius}
    </div>
  );
};

interface SquareProps {
  sideLength: number;
}

const Square: React.FC<SquareProps> = ({ sideLength }) => {
  return (
    <div style={{ width: `${sideLength}px`, height: `${sideLength}px`, backgroundColor: 'red' }}>
      Square with side length {sideLength}
    </div>
  );
};

const FunctionCall: React.FC<any> = ({ functionData }) => {
  const { functionName, parameters } = functionData;

  // Generate JSX based on the function name and parameters
  const renderComponent = () => {
    switch (functionName) {
      case 'createCircle':
        return <Circle radius={parameters.radius} />;
      case 'createSquare':
        return <Square sideLength={parameters.sideLength} />;
      default:
        return null;
    }
  };

  return (
    <div>
      {renderComponent()}
    </div>
  );
};
export default function Home() {

    // const client = new OpenAI({
    //     apiKey: 'sk-proj-WffoeJpUSYeTPrGVJYrXT3BlbkFJ1LlOun7BhX5SlECdPnTx',
    //     dangerouslyAllowBrowser: true
    // });

    // // Define the conversation prompt with function calls
    // const conversation = [
    //   { role: 'user', content: 'Create a circle with radius 10' },
    // ];

    

  // Generate chat completion with function calls
  const generateCompletion = async () => {
    console.log(process.env.OPENAI_KEY);
    const tools = [
      {
        type: "function",
        function: {
          name: "createCircle",
          description: "Create a circle with the given radius",
          parameters: {
            type: "object",
            properties: {
              radius: {
                type: "number",
                description: "Radius of the circle",
              },
              unit: { type: "number"},
            },
            required: ["radius"],
          },
        },
      },
      {
        type: "function",
        function: {
          name: "createSquare",
          description: "Create a square with the given side length",
          parameters: {
            type: "object",
            properties: {
              sideLength: {
                type: "number",
                description: "length of side of the square",
              },
              unit: { type: "number"},
            },
            required: ["sideLength"],
          },
        },
      }
    ];

    return groq.chat.completions.create({
      messages: [
          {
              role: "system",
              content: "you are a helpful assistant."
          },

          {
              role: "user",
              content: "Create a circle with radius 10"
          }
      ],
      
      tools: tools,
      model: "llama3-8b-8192",
      temperature: 0,
      max_tokens: 1024,
      top_p: 1,
      stop: null,
      stream: false
  });
  };

  // State to hold the components returned by function calls
  const [functionComponents, setFunctionComponents] = useState<JSX.Element[]>([]);

  // Load the components returned by function calls when the component mounts
  useEffect(() => {
    const loadFunctionComponents = async () => {
      const components = await generateCompletion();
    // if (components && components.choices && components.choices.length > 0) {
    //   const renderedComponents = components.choices.map(choice => {
    //     const functionName = choice.metadata.function_name;
    //     const parameters = choice.metadata.parameters;
    //     switch (functionName) {
    //       case 'createCircle':
    //         return <Circle key={choice.id} radius={parameters.radius} />;
    //       case 'createSquare':
    //         return <Square key={choice.id} sideLength={parameters.sideLength} />;
    //       default:
    //         return null;
    //     }
    //   });
    //   setFunctionComponents(renderedComponents);
    // }
    if(components){
        setFunctionComponents(components);
    }
    };
    loadFunctionComponents();
  }, []);

    return (
        <div style={{ position: 'fixed', inset: 0 }}>
            ksdjnvi
            
            {/* <Tldraw
                persistenceKey="things-on-the-canvas-example"
                components={{
                    InFrontOfTheCanvas: useCallback(() => {
                        return (
                            // <FloatButton
                            //     type="primary"
                            //     icon={
                            //         <AudioOutlined
                            //             style={{ fontSize: '20px' }}
                            //         />
                            //     }
                            //     style={{
                            //         position: 'absolute',
                            //         width: 80,
                            //         height: 80,
                            //         bottom: 100,
                            //         left: 10,
                            //     }}
                            // />
                            <PlaceText text="Hello!" x={100} y={50}/>
                            
                            
                        );
                    }, []),
                }}
            /> */}
            {/* {functionComponents} */}
        </div>
    );
}
