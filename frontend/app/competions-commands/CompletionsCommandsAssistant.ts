import { Editor } from 'tldraw';
import OpenAI from 'openai';
import { ChatCompletionStream } from 'openai/lib/ChatCompletionStream.mjs';
import { Assistant, Thread } from '../assistant';
import { fetchText } from '../lib/fetchText';
import { assert } from '../lib/utils';
import { EditorDriverApi } from './EditorDriverApi';
import fs from 'fs';

import { getUserMessage } from './getUserMessage';
const Groq = require("groq-sdk");
const groq = new Groq({apiKey: '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', dangerouslyAllowBrowser: true});


const openai = new OpenAI({
    // apiKey: 'sk-proj-mC5TasNOgOIAClipprJJT3BlbkFJ4TlALxdlUl8bTBbiSsP0',
    apiKey: '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',
    baseURL: 'https://api.groq.com/openai/v1/',
    dangerouslyAllowBrowser: true,
});

export class CompletionCommandsAssistant
    implements Assistant<ChatCompletionStream>
{
    constructor() {}

    systemPrompt: string | null = null;

    getDefaultSystemPrompt(): Promise<string> {
        return fetchText();
    }

    async setSystemPrompt(prompt: string) {
        this.systemPrompt = prompt;
    }

    async createThread(editor: Editor) {
        const systemPrompt =
            this.systemPrompt ?? (await this.getDefaultSystemPrompt());
        return new CompletionCommandsThread(systemPrompt, editor);
    }
}

export class CompletionCommandsThread implements Thread<ChatCompletionStream> {
    messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[];

    constructor(systemPrompt: string, readonly editor: Editor) {
        this.messages = [
            {
                role: 'system',
                content: systemPrompt,
            },
        ];
    }

    getUserMessage(input: string) {
        return getUserMessage(this.editor, input);
    }

    currentStream: ChatCompletionStream | null = null;

    async sendMessage(userMessage: string) {
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
        if (this.currentStream) {
            this.messages.pop();
            await this.cancel();
        }

        const data = fs.readFileSync('./transcript.txt', 'utf8');
        console.log(data);

        this.messages.push({
            role: 'user',
            content: userMessage,
        });

        const stream = openai.beta.chat.completions.stream({
            model: 'llama3-70b-8192',
            // model: 'gpt-4',
            messages: this.messages,
        });

        console.log(stream);
        this.currentStream = stream;
        
        // const groq_response = await groq.chat.completions.create({
        //     // messages: [
        //     //     {
        //     //         role: "system",
        //     //         content: "you are a helpful assistant."
        //     //     },
                
        //     //     {
        //     //         role: "user",
        //     //         content: "Create a circle with radius 10"
        //     //     }
        //     // ],
        //     messages: this.messages,
            
        //     // tools: tools,
        //     model: "llama3-70b-8192",
        //     temperature: 0,
        //     max_tokens: 1024,
        //     top_p: 1,
        //     stop: null,
        //     stream: true
        // });
        
        // console.log(groq_response)
        // this.currentStream = groq_response;
        

        return stream;
    }

    async cancel() {
        if (this.currentStream) {
            this.currentStream.abort();
            this.currentStream = null;
        }
    }

    async handleAssistantResponse(stream: ChatCompletionStream) {
        assert(this.currentStream === stream);

        const api = new EditorDriverApi(this.editor);

        return new Promise<void>((resolve, reject) => {
            stream.on('content', (_delta, snapshot) => {
                if (stream.aborted) return;

                // Tell the driver API to process the whole snapshot
                api.processSnapshot(snapshot);
            });

            stream.on('finalContent', (snapshot) => {
                if (stream.aborted) return;

                // Tell the driver API to complete
                api.complete();

                // Add the assistant's response to the thread
                this.messages.push({
                    role: 'assistant',
                    content: snapshot,
                });
                resolve();
                this.currentStream = null;
            });

            stream.on('abort', () => {
                reject(new Error('Stream aborted'));
                this.currentStream = null;
            });

            stream.on('error', (err) => {
                console.error(err);
                reject(err);
                this.currentStream = null;
            });

            stream.on('end', () => {
                resolve();
                this.currentStream = null;
            });
        });
    }
}
