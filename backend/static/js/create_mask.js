function create_string_mask(selector) {
    return IMask(document.querySelector(selector), {
        mask: `[${'a'.repeat(20)}] [${'a'.repeat(20)}] [${'a'.repeat(20)}]`
    })
}

function create_date_mask(selector) {
    return IMask(document.querySelector(selector), {
            mask: Date,
            pattern: 'DD.MM.YYYY',
            blocks: {
                YYYY: {
                    mask: IMask.MaskedRange,
                    from: 1900,
                    to: 9999
                },
                MM: {
                    mask: IMask.MaskedRange,
                    from: 1,
                    to: 12
                },
                DD: {
                    mask: IMask.MaskedRange,
                    from: 1,
                    to: 31
                },
            }
        })
}

function create_time_mask(selector) {
    return IMask(document.querySelector(selector), {
            mask: Date,
            pattern: 'HH:MM',
            blocks: {
                HH: {
                    mask: IMask.MaskedRange,
                    from: 0,
                    to: 23
                },
                MM: {
                    mask: IMask.MaskedRange,
                    from: 0,
                    to: 590
                }
            }
        })
}