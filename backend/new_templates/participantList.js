let startX, movingX, deltaX;
let endX = 0
let infos = document.getElementsByClassName("participantInfo")
let mouseDown = false;
for (let participantInfo of infos) {
    participantInfo.ontouchstart = (event) => {
        touchStart(event, participantInfo)
    }
    participantInfo.ontouchmove = (event) => {
        touchMove(event, participantInfo)
    }
    participantInfo.ontouchend = () => {
        touchEnd(participantInfo)
    }
    participantInfo.onmousedown = (event) => {
        mouseDown = true
        mouseStart(event, participantInfo)
    }
    participantInfo.onmousemove = (event) => {
        if (mouseDown) {
            mouseMove(event, participantInfo)
        }
    }
    participantInfo.onmouseup = () => {
        mouseDown = false
        touchEnd(participantInfo)
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
        }, 1000)
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