const timezone = document.querySelector("#time-zone")
const timezone_input = document.querySelector("#time-zone-input")
const timezone_selector = document.querySelector(".field__selector")

const timezone_items = document.querySelectorAll(".selector__item")

function sort_selector(input) {
    timezone_items.forEach((item) => {
        let string = item.innerText.toLowerCase()
        if (!string.includes(input.toLowerCase())) {
            item.classList.add("hidden")
        } else {
            item.classList.remove("hidden")
        }
    })

}

timezone_input.onfocus = () => {
    timezone_selector.classList.remove("wrapped");
    sort_selector(timezone_input.value)
}

timezone_input.oninput = () => {
    sort_selector(timezone_input.value)
}

timezone_input.onblur = () => {
    let wrap = () => {
        timezone_selector.classList.add("wrapped");
    }
    setTimeout(wrap, 100)
}


timezone_items.forEach((item) => {

    let update = () => {
        timezone_input.value = item.innerText
        timezone.value = item.value

    };

    item.onclick = update

    item.ontouchend = update

})