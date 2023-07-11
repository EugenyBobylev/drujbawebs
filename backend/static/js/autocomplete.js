function autocomplete(selector, value, mask = null) {
    if (value) {
        document.querySelector(selector).value = value;
        if (typeof document.querySelector(selector).update === 'function') {
            document.querySelector(selector).update()
        }
        if (mask !== null) {
            mask.updateValue()
        }
    }
}