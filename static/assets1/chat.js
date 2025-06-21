document.addEventListener('DOMContentLoaded', () => {
    // These variables must be set in the template that includes this JS file
    const username = window.CHAT_USERNAME;
    const roomName = window.CHAT_ROOMNAME;
    const userImage = window.CHAT_USERIMAGE;
    const otherUserImage = window.CHAT_OTHERUSERIMAGE || '/media/default.jpg';

    const chatSocket = new WebSocket(
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
        window.location.host + '/ws/directs/' + roomName + '/'
    );

    const chatMessages = document.querySelector('.chat-messages');

    chatSocket.onopen = () => console.log('WebSocket connected ✅');
    chatSocket.onerror = e => console.error('WebSocket error ❌', e);
    chatSocket.onclose = e => console.warn('WebSocket closed ⚠️', e);

    chatSocket.onmessage = e => {
        const data = JSON.parse(e.data);
        const messageDiv = document.createElement('div');

        const senderImage = (data.sender === username) ? userImage : otherUserImage;
        const alignClass = (data.sender === username) ? 'chat-message-right' : 'chat-message-left';

        messageDiv.className = `${alignClass} pb-2`;
        messageDiv.innerHTML = `
            <div>
                <img src="${senderImage}" class="rounded-circle mr-1" width="40" height="40">
                <div class="text-muted small text-nowrap mt-2" style="font-size:10px;">Now</div>
            </div>
            <div class="flex-shrink-1 bg-light rounded py-2 px-3 ml-3">
                ${data.message}
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const input = document.querySelector('input[name="body"]');
            const message = input.value.trim();
            if (!message) return;

            // Send via WebSocket
            chatSocket.send(JSON.stringify({
                'message': message,
                'sender': username
            }));

            // Save via Django view
            await fetch(window.CHAT_SEND_URL, {
                method: "POST",
                headers: {
                    "X-CSRFToken": window.CHAT_CSRF_TOKEN,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `to_user=${roomName}&body=${encodeURIComponent(message)}`
            });

            input.value = '';
        });
    }

    // Auto-scroll to latest on load
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
}); 
