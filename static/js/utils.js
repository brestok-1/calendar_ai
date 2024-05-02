const sendButton = document.getElementById('sendButton')
const textInput = document.getElementById('textInput')

function createNewMessage(text, type) {
    const message = document.createElement('div')
    message.className = 'message'
    let content = document.createElement('div')
    content.style.whiteSpace = "pre-line"
    if (type === 'bot') {
        content.className = 'bot_message mt-4 py-3 px-4 rounded-4 w-75 ms-3'
    } else {
        content.className = 'user_message mt-4 py-3 px-4 rounded-4 w-75 me-3'
    }
    content.innerText = text
    message.appendChild(content)
    chatBody.appendChild(message)
}

function sendMessageToServer() {
    const userQuery = textInput.value;
    if (userQuery.length === 0) {
        return
    }
    createNewMessage(userQuery, 'user')
    socket.send(JSON.stringify({'query': userQuery, 'country': "Undefined"}));
    textInput.value = ''
    isFirstWord = false
    chatBody.scrollTop = chatBody.scrollHeight;
}

function generateUUID() {
    const arr = new Uint8Array(16);
    window.crypto.getRandomValues(arr);

    arr[6] = (arr[6] & 0x0f) | 0x40;
    arr[8] = (arr[8] & 0x3f) | 0x80;

    return ([...arr].map((b, i) =>
        (i === 4 || i === 6 || i === 8 || i === 10 ? "-" : "") + b.toString(16).padStart(2, "0")
    ).join(""));
}

textInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessageToServer();
    }
});

sendButton.addEventListener("click", sendMessageToServer);


function enrichAIResponse(botMessageElement) {
    const links = botMessageElement.querySelectorAll('.extraDataLink');

    links.forEach(link => {
        const tooltip = link.nextElementSibling;
        link.addEventListener('mouseenter', function () {
            tooltip.style.display = 'block';
            const tooltipWidth = parseInt(link.offsetWidth) * 2
            tooltip.style.width = tooltipWidth + 'px'

            const tooltipImg = tooltip.querySelector('.tooltip-img')
            if (tooltipImg) {
                tooltipImg.width = tooltipWidth - 16
            }
            const linkRect = this.getBoundingClientRect();
            if (linkRect.top < tooltip.offsetHeight + 4) {
                tooltip.style.top = (window.scrollY + linkRect.bottom + 4) + 'px';
            } else {
                tooltip.style.top = (window.scrollY + linkRect.top - tooltip.offsetHeight - 4) + 'px';
            }
            tooltip.style.left = (linkRect.left + (linkRect.width / 2) - (tooltipWidth / 2)) + 'px';
        });

        link.addEventListener('mouseleave', function () {
            setTimeout(() => {
                if (!tooltip.matches(':hover')) {
                    tooltip.style.display = 'none';
                }
            }, 300)
        });

        tooltip.addEventListener('mouseleave', function () {
            this.style.display = 'none';
        });
    });
}
