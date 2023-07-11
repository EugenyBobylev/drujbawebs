function create_calendar(selector, mask) {
    let date = document.querySelector(selector)
    let date_input = document.querySelector(selector + "-input")

    date.update = () => {
        let [year, month, day] = date.value.split("-")
        date_input.value = `${day}.${month}.${year}`
        mask.updateValue()
    }

    date_input.update = () => {
        let [day, month, year] = date_input.value.split(".")
        date.value = `${year}-${month}-${day}`
    }
}