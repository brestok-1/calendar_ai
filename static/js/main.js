const chatBody = document.getElementById('chatBody')
const timezone = new Intl.DateTimeFormat('en-Us', {timeZoneName: 'long'}).resolvedOptions().timeZone;
let socket

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


async function init() {
    console.log(credentials)
    socket = new WebSocket(`ws://127.0.0.1:8000/ws/prediction/${timezone}`)
    socket.onopen = (event) => {
        socket.send(JSON.stringify({
            "type": "initialization",
            "credentials": credentials
        }))
    }
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        const message_type = data['type']
        let assistantMessage = data['data']['text']
        if (message_type === 'messaging') {
            createNewMessage(assistantMessage, 'assistant')
        } else if (message_type === 'suggestion') {
            const events = data['data']['events']
            createNewMessage(assistantMessage, 'assistant')
            createNewMessage(events, 'assistant')
        }
    }
}

(async function () {
    await init()
})();
