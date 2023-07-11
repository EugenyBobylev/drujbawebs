const timezone = document.querySelector("#time-zone")
const timezone_input = document.querySelector("#time-zone-input")
const timezone_selector = document.querySelector(".field__selector")

const timezone_items = document.querySelectorAll(".selector__item")

timezone.onchange = () => {
    timezone_items.forEach((item) => {
        if (item.value == timezone.value) {
                timezone_input.value = item.innerText
        }
    })
}

timezone_input.onfocus = () => {
    timezone_selector.classList.remove("wrapped");
}


timezone_items.forEach((item) => {

    let update = () => {
        timezone.value = item.value
        timezone.onchange()
        timezone_selector.classList.add("wrapped");
        timezone_input.blur()
    };

    const isTouch = () => 'ontouchstart' in window || window.DocumentTouch && document instanceof window.DocumentTouch || navigator.maxTouchPoints > 0 || window.navigator.msMaxTouchPoints > 0

    item.addEventListener('mousedown', (e) => {
      if (isTouch())  {
          update()
      }
    });

    item.onclick = update

})