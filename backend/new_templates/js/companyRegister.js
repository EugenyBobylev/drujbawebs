const companyRegister = document.querySelector('.companyRegister')

companyRegister.addEventListener('submit', (e)=>{
    e.preventDefault()
    const el = e.target

    fetch(`${API__companyREGISTER}`,{
        method: 'POST',
        headers: {
        'Content-type': 'application/json', // qysi formatta yuborish
        'Accept': 'application/json', // qysi formatta uni qabul qilib olishi
        'Access-Control-Allow-Origin': '*' // ruxsat berish hammaga
        },
        body:JSON.stringify({
            company_name: el.company_name.value,
            activity: el.activity.value,
            peoples: el.peoples.value,
            name: el.name.value,
            job: el.job.value,
            contact: el.contact.value,
            mail: el.mail.value,
        })
    })
    .then((res)=> res.json())
    .then((data)=> console.log(data))
})