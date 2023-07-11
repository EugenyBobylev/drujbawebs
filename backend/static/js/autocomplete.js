function autocomplete(selector, value, mask = null) {
    if (value) {
        document.querySelector(selector).value = value;
        if (typeof document.querySelector(selector).onchange === 'function') {
            document.querySelector(selector).onchange()
        }
        if (mask !== null) {
            mask.updateValue()
        }
    }
}