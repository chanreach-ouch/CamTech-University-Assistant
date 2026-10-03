(function() {
    // 1. Inject Theme Stylesheet if not already injected
    if (!document.getElementById('camtech-widget-styles')) {
        const link = document.createElement('link');
        link.id = 'camtech-widget-styles';
        link.rel = 'stylesheet';
        link.href = '/widget.css?v=' + Date.now();
        document.head.appendChild(link);
    }

    // 2. Ensure marked.js is available for rich markdown rendering
    if (typeof marked === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
        document.head.appendChild(script);
    }

    // SVG Icons
    const ICONS = {
        chat: `<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>`,
        close: `<svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`,
        mortarboard: `<svg viewBox="0 0 24 24"><path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/></svg>`,
        refresh: `<svg viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>`,
        send: `<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`,
        doc: `<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>`
    };

    // 3. Build Widget DOM
    const btn = document.createElement('button');
    btn.id = 'chat-widget-btn';
    btn.setAttribute('aria-label', 'Open CamTech University Assistant');
    btn.innerHTML = `${ICONS.chat}<span class="chat-widget-badge"></span>`;

    const panel = document.createElement('div');
    panel.id = 'chat-widget-panel';
    panel.innerHTML = `
        <div id="chat-widget-header">
            <div class="chat-header-brand">
                <div class="chat-header-avatar">
                    ${ICONS.mortarboard}
                </div>
                <div class="chat-header-titles">
                    <span class="chat-header-title">CamTech Assistant</span>
                    <span class="chat-header-status">Admissions & Academic Advisory</span>
                </div>
            </div>
            <div class="chat-header-actions">
                <button class="chat-action-btn" id="chat-widget-reset" title="New conversation">
                    ${ICONS.refresh}
                </button>
                <button class="chat-action-btn" id="chat-widget-close" title="Close assistant">
                    ${ICONS.close}
                </button>
            </div>
        </div>
        <div id="chat-widget-messages"></div>
        <div id="chat-widget-input-area">
            <input type="text" id="chat-widget-input" placeholder="Ask about majors, scholarships, tuition..." autocomplete="off">
            <button id="chat-widget-send" title="Send message" aria-label="Send">
                ${ICONS.send}
            </button>
        </div>
    `;

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    // 4. Element Selectors & Session
    const msgs = document.getElementById('chat-widget-messages');
    const input = document.getElementById('chat-widget-input');
    const sendBtn = document.getElementById('chat-widget-send');
    const closeBtn = document.getElementById('chat-widget-close');
    const resetBtn = document.getElementById('chat-widget-reset');

    function getThreadId(forceNew = false) {
        let tid = localStorage.getItem('camtech_thread_id');
        if (!tid || forceNew) {
            tid = "user-" + Math.random().toString(36).substring(2, 9) + "-" + Date.now();
            localStorage.setItem('camtech_thread_id', tid);
        }
        return tid;
    }

    let threadId = getThreadId();

    // 5. Render Welcome Card with Starter Chips
    function renderWelcome() {
        msgs.innerHTML = `
            <div class="chat-welcome-card">
                <div class="chat-welcome-title">CamTech University Inquiry Desk</div>
                <div class="chat-welcome-desc">
                    Official advisory service for undergraduate and graduate programs, entrance exams, scholarships, and tuition fee schedules.
                </div>
                <div class="chat-prompt-chips">
                    <button class="prompt-chip" data-prompt="What majors and degree programs are offered at CamTech?">
                        <span class="chip-arrow">→</span> What majors are offered?
                    </button>
                    <button class="prompt-chip" data-prompt="How can I apply for scholarships at CamTech University?">
                        <span class="chip-arrow">→</span> Scholarship opportunities & how to apply
                    </button>
                    <button class="prompt-chip" data-prompt="What is the admission and entrance exam process?">
                        <span class="chip-arrow">→</span> Admission & entrance exam process
                    </button>
                    <button class="prompt-chip" data-prompt="What are the tuition fees for undergraduate programs?">
                        <span class="chip-arrow">→</span> Tuition fees overview
                    </button>
                </div>
            </div>
        `;

        // Attach chip click handlers
        msgs.querySelectorAll('.prompt-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const prompt = chip.getAttribute('data-prompt');
                if (prompt) {
                    input.value = prompt;
                    sendMessage();
                }
            });
        });
    }

    renderWelcome();

    // 6. Open / Close Behavior
    let isOpen = false;
    function toggleWidget(show) {
        isOpen = (show !== undefined) ? show : !isOpen;
        if (isOpen) {
            panel.classList.add('open');
            btn.innerHTML = ICONS.close;
            setTimeout(() => input.focus(), 250);
        } else {
            panel.classList.remove('open');
            btn.innerHTML = `${ICONS.chat}<span class="chat-widget-badge"></span>`;
        }
    }

    btn.onclick = () => toggleWidget();
    closeBtn.onclick = () => toggleWidget(false);

    // 7. Reset Conversation
    resetBtn.onclick = () => {
        if (confirm("Start a new conversation?")) {
            threadId = getThreadId(true);
            renderWelcome();
            input.value = '';
            input.focus();
        }
    };

    // 8. Append Messages
    function appendMessage(role, text, sources) {
        const div = document.createElement('div');
        div.className = `chat-msg ${role}`;

        // Parse markdown for bot messages
        if (role === 'bot') {
            if (typeof marked !== 'undefined') {
                div.innerHTML = marked.parse(text);
            } else {
                div.innerText = text;
            }

            // Append polished source badges if present
            if (sources && sources.length > 0) {
                const srcContainer = document.createElement('div');
                srcContainer.className = 'chat-sources-container';
                
                const srcHeader = document.createElement('div');
                srcHeader.className = 'chat-sources-header';
                srcHeader.innerText = 'Sources Referenced';
                srcContainer.appendChild(srcHeader);

                const srcList = document.createElement('div');
                srcList.className = 'chat-sources-list';
                
                sources.forEach(src => {
                    const badge = document.createElement('span');
                    badge.className = 'source-badge';
                    badge.title = src;
                    const cleanName = src.replace(/^zh_hans_|^kh_/, '').replace(/\.md$|\.pdf$/, '');
                    badge.innerHTML = `${ICONS.doc} <span>${cleanName}</span>`;
                    srcList.appendChild(badge);
                });

                srcContainer.appendChild(srcList);
                div.appendChild(srcContainer);
            }
        } else {
            div.innerText = text;
        }

        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    }

    // 9. Send Message
    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;

        appendMessage('user', text);

        // Render Animated Typing Indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-msg bot';
        loadingDiv.id = 'chat-loading-indicator';
        loadingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        msgs.appendChild(loadingDiv);
        msgs.scrollTop = msgs.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: threadId, message: text })
            });

            const data = await res.json();
            const loader = document.getElementById('chat-loading-indicator');
            if (loader) loader.remove();

            appendMessage('bot', data.response, data.sources);
        } catch (e) {
            const loader = document.getElementById('chat-loading-indicator');
            if (loader) loader.remove();
            appendMessage('bot', 'Sorry, I encountered an issue connecting to the university server. Please try again.');
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    sendBtn.onclick = sendMessage;
    input.onkeypress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    };
})();
