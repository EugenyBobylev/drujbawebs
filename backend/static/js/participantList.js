let startX, movingX, deltaX;
let itemContents = document.getElementsByClassName("itemContent")
let mouseDown = false;

for (let itemContent of itemContents) {
    itemContent.ontouchstart = (event) => {
        touchStart(event, itemContent)
    }
    itemContent.ontouchmove = (event) => {
        touchMove(event, itemContent)
    }
    itemContent.ontouchend = () => {
        touchEnd(itemContent)
    }
    itemContent.onmousedown = (event) => {
        mouseDown = true
        mouseStart(event, itemContent)
    }
    itemContent.onmousemove = (event) => {
        if (mouseDown) {
            mouseMove(event, itemContent)
        }
    }

    itemContent.onmouseup = () => {
        mouseDown = false
        touchEnd(itemContent)
    }
}

function touchStart(e, participantInfo) {
    participantInfo.style.transition = "0s"
    startX = e.touches[0].clientX
}

function touchMove(e, participantInfo) {
    e.stopPropagation();
    movingX = e.touches[0].clientX
    deltaX = movingX - startX
    if (deltaX <= -48) {
        deltaX = -48
    }
    if (deltaX < 0) {
        participantInfo.style.transform = "translateX(" + deltaX + "px)"
    }
}

function touchEnd(participantInfo) {
    if (deltaX <= -48) {
        setTimeout(() => {
            participantInfo.style.transition = "0.3s"
            participantInfo.style.transform = "translateX(-" + 0 + "px)"
        }, 3000)
    } else {
        participantInfo.style.transition = "0.3s"
        participantInfo.style.transform = "translateX(-" + 0 + "px)"
    }

}

function mouseStart(e, participantInfo) {
    participantInfo.style.transition = "0s"
    startX = e.clientX
}

function mouseMove(e, participantInfo) {
    e.stopPropagation();
    movingX = e.clientX
    deltaX = movingX - startX
    if (deltaX <= -48) {
        deltaX = -48
    }
    if (deltaX < 0) {
        participantInfo.style.transform = "translateX(" + deltaX + "px)"
    }
}