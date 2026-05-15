import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const ChatPage = () => {
    const navigate = useNavigate();
    const [input, setInput] = useState('');

    // Dữ liệu chat giả lập
    const [messages, setMessages] = useState([
        { id: 1, sender: 'ai', text: 'Chào bạn! Tôi là Lancer AI. Hôm nay chúng ta sẽ phỏng vấn cho vị trí Frontend Developer. Bạn đã sẵn sàng chưa?' },
        { id: 2, sender: 'user', text: 'Chào bạn, tôi đã sẵn sàng!' },
        { id: 3, sender: 'ai', text: 'Tuyệt vời. Câu hỏi đầu tiên: Bạn có thể giải thích sự khác biệt giữa state và props trong React không?' }
    ]);

    const handleSend = () => {
        if (!input.trim()) return;
        // Thêm tin nhắn user
        setMessages([...messages, { id: Date.now(), sender: 'user', text: input }]);
        setInput('');
        
        // Giả lập AI phản hồi sau 1 giây
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now(), sender: 'ai', text: 'Cảm ơn câu trả lời của bạn. Chúng ta tiếp tục nhé...' }]);
        }, 1000);
    };

    const styles = {
        container: { maxWidth: '800px', margin: '20px auto', height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column', fontFamily: 'system-ui', color: 'var(--text-color)' },
        chatBox: { flex: 1, overflowY: 'auto', padding: '20px', background: 'var(--bg-color)', border: '1px solid var(--border-color)', borderRadius: '12px 12px 0 0', display: 'flex', flexDirection: 'column', gap: '15px' },
        messageWrapper: (isUser) => ({ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }),
        bubble: (isUser) => ({
            maxWidth: '70%', padding: '12px 16px', borderRadius: '16px', lineHeight: '1.5',
            // User dùng màu #3182ce chữ trắng, AI dùng màu nền phụ chữ theo theme
            background: isUser ? '#3182ce' : 'var(--nav-bg)',
            color: isUser ? 'white' : 'var(--text-color)',
            border: isUser ? 'none' : '1px solid var(--border-color)',
            borderBottomRightRadius: isUser ? '4px' : '16px',
            borderBottomLeftRadius: !isUser ? '4px' : '16px',
        }),
        inputArea: { display: 'flex', padding: '15px', background: 'var(--nav-bg)', border: '1px solid var(--border-color)', borderTop: 'none', borderRadius: '0 0 12px 12px', gap: '10px' },
        input: { flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', outline: 'none' },
        btnSend: { background: '#3182ce', color: 'white', padding: '0 20px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
        backBtn: { background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '5px', fontSize: '16px' }
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <button style={styles.backBtn} onClick={() => navigate(-1)}>← Quay lại</button>
                
                <div style={styles.chatBox}>
                    {messages.map(msg => (
                        <div key={msg.id} style={styles.messageWrapper(msg.sender === 'user')}>
                            <div style={styles.bubble(msg.sender === 'user')}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                </div>

                <div style={styles.inputArea}>
                    <input 
                        style={styles.input} 
                        placeholder="Nhập câu trả lời của bạn..." 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <button style={styles.btnSend} onClick={handleSend}>Gửi 🚀</button>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;