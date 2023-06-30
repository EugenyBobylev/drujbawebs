let tg = window.Telegram.WebApp;
let api_url = "https://panel.druzhba.io/";
// let api_url = "https://49dc-178-66-156-95.ngrok-free.app/";

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
        tg.showAlert(JSON.stringify(r))
        tg.close()
    }).catch(err => tg.showAlert('err'))
}

function closeWebApp() {
    tg.close()
}
