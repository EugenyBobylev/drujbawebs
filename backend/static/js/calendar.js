const extra_fields = ["#event-date", "#congratulation-date"]

function date_over_now_validator(selector, data) {
    if (extra_fields.includes(selector)) {
        let [year, month, day] = data
        let chosen_date = new Date(year, month - 1, day)
        chosen_date.setDate(chosen_date.getDate() + 1);
        if (chosen_date < new Date()) {
            alert("Введите актуальную дату")
            return false
        }
    }
    return true
}

function create_calendar(selector, mask) {
    let date = document.querySelector(selector)
    let date_input = document.querySelector(selector + "-input")

    date.onchange = () => {
        let [year, month, day] = date.value.split("-")
        if (date_over_now_validator(selector, [year, month, day])) {
            date_input.value = `${day}.${month}.${year}`
            mask.updateValue()
        } else {
            date_input.onchange()
        }
    }

    date_input.onchange = () => {
        let [day, month, year] = date_input.value.split(".")
        if (date_over_now_validator(selector, [year, month, day])) {
            date.value = `${year}-${month}-${day}`
        } else {
            date.onchange()
        }
    }
}