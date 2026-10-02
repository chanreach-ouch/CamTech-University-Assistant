(function() {
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/widget.css';
    document.head.appendChild(link);

    // Build DOM
    const btn = document.createElement('button');
    btn.id = 'chat-widget-btn';
    btn.innerHTML = '💬';
    
    const panel = document.createElement('div');
    panel.id = 'chat-widget-panel';
    panel.innerHTML = `
        <div id="chat-widget-header">
            <span>CamTech Assistant</span>
            <button id="chat-widget-close" style="background:none;border:none;color:white;cursor:pointer;">✖</button>
        </div>
        <div id="chat-widget-messages"></div>
        <div id="chat-widget-input-area">
            <input type="text" id="chat-widget-input" placeholder="Ask a question...">
            <button id="chat-widget-send">Send</button>
        </div>
    `;

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    // Logic
    const msgs = document.getElementById('chat-widget-messages');
    const input = document.getElementById('chat-widget-input');
    const sendBtn = document.getElementById('chat-widget-send');
    
    let threadId = localStorage.getItem('camtech_thread_id');
    if (!threadId) {
        threadId = "user-" + Math.random().toString(36).substring(7);
        localStorage.setItem('camtech_thread_id', threadId);
    }

    btn.onclick = () => {
        panel.style.display = panel.style.display === 'flex' ? 'none' : 'flex';
        if(panel.style.display === 'flex') input.focus();
    };

    document.getElementById('chat-widget-close').onclick = () => {
        panel.style.display = 'none';
    };

    function appendMessage(role, text, sources) {
        const div = document.createElement('div');
        div.className = `chat-msg ${role}`;
        div.innerText = text;
        
        if (sources && sources.length > 0) {
            const srcSpan = document.createElement('span');
            srcSpan.className = 'chat-source';
            srcSpan.innerText = 'Sources: ' + sources.join(', ');
            div.appendChild(srcSpan);
        }
        
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    }

    async function sendMessage() {
        const text = input.value.trim();
        if(!text) return;
        
        input.value = '';
        appendMessage('user', text);
        
        try {
            const res = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({thread_id: threadId, message: text})
            });
            const data = await res.json();
            appendMessage('bot', data.response, data.sources);
        } catch (e) {
            appendMessage('bot', 'Error connecting to server.');
        }
    }

    sendBtn.onclick = sendMessage;
    input.onkeypress = (e) => { if(e.key === 'Enter') sendMessage(); };
})();
