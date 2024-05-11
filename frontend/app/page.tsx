'use client';

import { useCallback } from 'react';
import { Tldraw } from 'tldraw';
import './index.css';
import { FloatButton } from 'antd';
import { AudioOutlined } from '@ant-design/icons';

export default function Home() {
    return (
        <div style={{ position: 'fixed', inset: 0 }}>
            <Tldraw
                persistenceKey="things-on-the-canvas-example"
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
                            />
                        );
                    }, []),
                }}
            />
        </div>
    );
}
