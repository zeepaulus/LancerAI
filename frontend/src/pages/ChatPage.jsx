import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const ChatPage = () => {
    const navigate = useNavigate();
    const [input, setInput] = useState('');
    const chatEndRef = useRef(null);

    const [messages, setMessages] = useState([
        { id: 1, sender: 'ai', text: 'Chào bạn! Tôi là Lancer AI. Hôm nay chúng ta sẽ phỏng vấn cho vị trí Frontend Developer. Bạn đã sẵn sàng chưa?' },
        { id: 2, sender: 'user', text: 'Chào bạn, tôi đã sẵn sàng!' },
        { id: 3, sender: 'ai', text: 'Tuyệt vời. Câu hỏi đầu tiên: Bạn có thể giải thích sự khác biệt giữa state và props trong React không?' }
    ]);

    // Auto-scroll to bottom
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;
        setMessages([...messages, { id: Date.now(), sender: 'user', text: input }]);
        setInput('');
        
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now(), sender: 'ai', text: 'Cảm ơn câu trả lời của bạn. Chúng ta tiếp tục nhé...' }]);
        }, 1000);
    };

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column'}}>
            <Navbar />
            <div style={styles.container}>
                <button className="btn-tertiary" style={{marginBottom: 'var(--sp-sm)'}} onClick={() => navigate(-1)}>
                    ← Quay lại
                </button>
                
                <div style={styles.chatBox}>
                    {messages.map(msg => {
                        const isUser = msg.sender === 'user';
                        return (
                            <div key={msg.id} style={{display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start'}}>
                                {!isUser && <div style={styles.aiAvatar}>AI</div>}
                                <div style={isUser ? styles.bubbleUser : styles.bubbleAI}>
                                    {msg.text}
                                </div>
                            </div>
                        );
                    })}
                    <div ref={chatEndRef} />
                </div>

                <div style={styles.inputArea}>
                    <input 
                        className="text-input"
                        style={{flex: 1, borderRadius: 'var(--rounded-pill)', paddingLeft: 'var(--sp-md)'}}
                        placeholder="Nhập câu trả lời của bạn..." 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <button className="btn-primary" onClick={handleSend}>
                        Gửi
                    </button>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: 'var(--sp-base) var(--sp-lg)',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - var(--nav-height))',
    },
    chatBox: {
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--sp-lg)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) 0 0',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-base)',
    },
    aiAvatar: {
        width: '32px',
        height: '32px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '11px',
        fontWeight: 600,
        color: 'var(--muted)',
        flexShrink: 0,
        marginRight: 'var(--sp-xs)',
        marginTop: '2px',
    },
    bubbleUser: {
        maxWidth: '70%',
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xs) var(--rounded-xl)',
        backgroundColor: 'var(--primary)',
        color: 'var(--on-primary)',
        fontSize: '15px',
        lineHeight: 1.5,
        letterSpacing: '0.15px',
    },
    bubbleAI: {
        maxWidth: '70%',
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xl) var(--rounded-xs)',
        backgroundColor: 'var(--surface-strong)',
        color: 'var(--body-strong, var(--ink))',
        fontSize: '15px',
        lineHeight: 1.5,
        letterSpacing: '0.15px',
        border: '1px solid var(--hairline)',
    },
    inputArea: {
        display: 'flex',
        padding: 'var(--sp-sm)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderTop: 'none',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        gap: 'var(--sp-xs)',
        alignItems: 'center',
    },
};

export default ChatPage;