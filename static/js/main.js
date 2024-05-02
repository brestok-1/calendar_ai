const chatBody = document.getElementById('chatBody')
const openButton = document.getElementById('toggleButton')
const chatbotWindow = document.getElementById('chatbotWindow');

let socket
let isFirstWord = false
let botMessage

window.addEventListener('load', adjustChatBodyHeight);
window.addEventListener('resize', adjustChatBodyHeight);

function getTotalHeight(element) {
    const styles = window.getComputedStyle(element);
    const margins = ['marginTop', 'marginBottom', 'borderTopWidth', 'borderBottomWidth']
        .reduce((acc, style) => acc + parseFloat(styles[style]), 0);
    return element.offsetHeight + margins;
}

function adjustChatBodyHeight() {
    const chatFooter = document.getElementById('chatFooter')
    const chatHeader = document.getElementById('chatHeader')
    const chatFooterHeight = getTotalHeight(chatFooter);
    const chatHeaderHeight = getTotalHeight(chatHeader);
    const viewportHeight = window.innerHeight - chatHeaderHeight - chatFooterHeight;
    chatBody.style.height = viewportHeight + 'px';
}

function openChatBotWindow() {
    let lastScrollHeight = chatBody.scrollHeight;
    const uuid = generateUUID()
    socket = new WebSocket(`ws://127.0.0.1:8000/ws/${uuid}`);
    socket.onclose = (event) => console.log('WebSocket disconnected', event);
    socket.onerror = (error) => {
        alert('Something was wrong. Try again later.')
        window.location.reload()
    };
    socket.onmessage = (event) => {
        if (chatBody.scrollHeight > lastScrollHeight) {
            chatBody.scrollTop = chatBody.scrollHeight;
            lastScrollHeight = chatBody.scrollHeight;
        }
        if (!isFirstWord) {
            isFirstWord = true
            createNewMessage(event.data, 'bot')
            const botMessages = document.querySelectorAll('.bot_message');
            botMessage = botMessages[botMessages.length - 1];
        } else {
            const aiMessage = event.data
            if (aiMessage.startsWith('ENRICHED:')) {
                console.log(aiMessage)
                botMessage.innerHTML = aiMessage.substring(9)
                enrichAIResponse(botMessage)
            } else {
                botMessage.innerHTML = aiMessage
            }
        }
    }
}

function closeChatBotWindow() {
    socket.close()
    chatbotWindow.style.visibility = 'hidden'
    openButton.style.display = 'block'
}

openButton.addEventListener('click', function () {
    chatbotWindow.style.visibility = "visible";
    openButton.style.display = 'none'
    openChatBotWindow();
});