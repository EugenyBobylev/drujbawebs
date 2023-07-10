const elRegisterByLink = document.querySelector('.registerByLink')


elRegisterByLink.addEventListener('submit', (e)=>{
    e.preventDefault()
    console.log(e.target.username.value);
    console.log(e.target.birthday.value);
    console.log(e.target.job.value);
    console.log(e.target.company.value);
    fetch(`${API__REGISTER}`,{
        method: 'POST',
        headers: {
        'Content-type': 'application/json', // qysi formatta yuborish
        'Accept': 'application/json', // qysi formatta uni qabul qilib olishi
        'Access-Control-Allow-Origin': '*' // ruxsat berish hammaga
        },
        body:JSON.stringify({name: e.target.username.value, birthday: e.target.birthday.value,timezone: e.target.timezone.value, job: e.target.job.value, company: e.target.company.value})
    })
    .then((res)=> res.json())
    .then((data)=> console.log(data))
})