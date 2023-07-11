const errors = {
    "birthdate": "Дата рождения введена не верно",
    "event_date": "Дата события введена не верно",
    "congratulation_date": "Дата поздравления введена не верно",
    "congratulation_time": "Время поздравления введено не верно"
}

async function ajaxSend(App, url, body, method) {

    await fetch(url, {
        method: method,
        mode: 'cors',
        headers: {
            'ngrok-skip-browser-warning': '100',
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'Authorization': btoa(App.initData),
        },
        body: JSON.stringify(body),
    }).then(res => {
        res.text().then(error => {
            let data = JSON.parse(error)
            if (res.status.toString() === '422') {
                data.detail.forEach((err) => {
                    let msg = errors[err.loc[1]]
                    if (msg) {
                        alert(msg)
                    }
                })
            } else {
                App.close()
            }
        })
    }).catch(err => {
        App.alert("error")
    })
}