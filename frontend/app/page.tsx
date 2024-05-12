'use client';

import { useMemo } from 'react';
import { useCallback } from 'react';
import { TLEditorComponents, Tldraw } from 'tldraw';
import './index.css';
import { FloatButton } from 'antd';
import { AudioOutlined } from '@ant-design/icons';
import { UserPrompt } from './components/user-prompt';
import { CompletionCommandsAssistant } from './competions-commands/CompletionsCommandsAssistant';

const components: TLEditorComponents = {
    InFrontOfTheCanvas: () => {
        const assistant = useMemo(() => new CompletionCommandsAssistant(), []);
        return <UserPrompt assistant={assistant} />;
    },
};

export default function Home() {
    return (
        <div style={{ position: 'fixed', inset: 0 }}>
            <Tldraw
                persistenceKey="blabbermouth"
                components={{
                    InFrontOfTheCanvas: useCallback(() => {
                        return (
                            <FloatButton
                                type="primary"
                                icon={
                                    <AudioOutlined
                                        style={{ fontSize: '20px' }}
                                    />
                                }
                                style={{
                                    position: 'absolute',
                                    width: 80,
                                    height: 80,
                                    bottom: 100,
                                    left: 10,
                                }}
                                onClick={() => {}}
                            />
                        );
                    }, []),
                }}
            />
        </div>
    );
}
