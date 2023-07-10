const timezone = document.querySelector("#time-zone")
const timezone_input = document.querySelector("#time-zone-input")
const timezone_selector = document.querySelector(".field__selector")

const timezone_items = document.querySelectorAll(".selector__item")

// function sort_selector(input) {
//     timezone_items.forEach((item) => {
//         let string = item.innerText.toLowerCase()
//         if (!string.includes(input.toLowerCase())) {
//             item.classList.add("hidden")
//         } else {
//             item.classList.remove("hidden")
//         }
//     })
//
// }

timezone_input.onfocus = () => {
    timezone_selector.classList.remove("wrapped");
}


timezone_items.forEach((item) => {

    let update = () => {
        timezone_input.value = item.innerText
        timezone.value = item.value
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

    // item.ontouchend = update

})