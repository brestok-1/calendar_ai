const chatBody = document.getElementById('chatBody')
const timezone = new Intl.DateTimeFormat('en-Us', {timeZoneName: 'long'}).resolvedOptions().timeZone;

console.log(timezone)
let chatId = localStorage.getItem('chat_id')
console.log(chatId)

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

async function getChatId() {
    const res = await fetch(
        "http://localhost:8000/chat/create", {
            method: 'GET',
        }
    )
    if (res.status === 307) {
        window.location = 'http://localhost:8000/login'
    }
    const result = await res.json()
    if (result.redirect) {
        window.location = result.redirect;
        return null;
    }
    console.log(result)
    return result['chat_id']
}

async function restoreMessageHistory(chatId) {
    const res = await fetch(
        `http://localhost:8000/message/history/${chatId}`, {
            method: 'GET',
        }
    )
    if (res.status === 307) {
        window.location = 'http://localhost:8000/login'
    }
    const result = await res.json()
    console.log(result)
    return result
}

async function init() {
    if (!chatId) {
        chatId = await getChatId()
        localStorage.setItem('chat_id', chatId)
    } else {
        const messages = await restoreMessageHistory(chatId)
        if (messages && messages.length > 0) {
            messages.forEach((message) => {
                createNewMessage(message['content'], message['role'])
            })
        }
    }
}

(async function () {
    await init()
})();
