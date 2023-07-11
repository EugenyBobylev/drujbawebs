function blur_items(pressed) {
    document.querySelectorAll(".form__item").forEach((item) => {
        if (pressed === item || item.contains(pressed)) {
            return
        } else {
            item.blur();
        }
    })
}
document.onclick = (event) => {
    blur_items(event.target)
}

document.ontouchend = (event) => {
    blur_items(event.target)
}