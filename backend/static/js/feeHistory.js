let tg = window.Telegram.WebApp;
let api_url = "https://panel.druzhba.io/";

async function openFund(id) {
    await fetch(`${api_url}api/fundraising/${id}/open/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'ngrok-skip-browser-warning': '100',
            'Content-Type': 'application/json',
            'Authorization': btoa(tg.initData),
        },
    }).then(r => {
        tg.close();
    }).catch(err => console.log('Ошибка запроса'))
}

function closeWebApp() {
    tg.close()
}
