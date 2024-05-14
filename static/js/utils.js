const sendButton = document.getElementById('sendButton')
const textInput = document.getElementById('textInput')

function createNewMessage(text, type) {
    const message = document.createElement('div')
    message.className = 'message'
    let content = document.createElement('div')
    content.style.whiteSpace = "pre-line"
    console.log(type)
    if (type === 'assistant') {
        content.className = 'bot_message mt-4 py-3 px-4 rounded-4 w-75 ms-3'
    } else {
        content.className = 'user_message mt-4 py-3 px-4 rounded-4 w-75 me-3'
    }
    content.innerText = text
    message.appendChild(content)
    chatBody.appendChild(message)
}

async function sendMessageToServer() {
    const userQuery = textInput.value;
    if (userQuery.length === 0) {
        return
    }
    createNewMessage(userQuery, 'user')
    textInput.value = ''
    const data = {
        "query": userQuery,
        "chat_id": parseInt(chatId),
        'timezone': timezone
    }
    const res = await fetch(
        "http://localhost:8000/message/create", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }
    )
    const result = await res.json();
    createNewMessage(result['response'], 'assistant')
    chatBody.scrollTop = chatBody.scrollHeight;
}

textInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessageToServer();
    }
});

sendButton.addEventListener("click", sendMessageToServer);

