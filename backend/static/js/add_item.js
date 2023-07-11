var mainItem = init_add_button(document.querySelector(".item__button_add"))
const item_list = document.querySelector(".form__item-list")

function init_add_button(button) {
    let item = button.parentElement

    button.onclick = () => {
        let new_item = button.parentElement.cloneNode(true)

        init_remove_button(button)
        init_add_button(new_item.querySelector(".item__button"))
        item_list.appendChild(new_item)

        let _id = `gift-${item_list.children.length}`
        new_item.querySelector(".form__field").value = ""
        new_item.querySelector(".form__field").id = _id

        new_item.querySelector(".field__placeholder").innerText = "Дополнительная ссылка"
        new_item.querySelector(".field__placeholder").setAttribute("for", _id)
        mainItem = new_item
    }
    return item
}

function init_remove_button(button) {
    button.classList.remove("item__button_add")
    button.classList.add("item__button_remove")
    button.onclick = () => {
        item_list.removeChild(button.parentElement)
    }
}