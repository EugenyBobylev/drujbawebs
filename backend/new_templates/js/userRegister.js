const elUserRegister =  document.querySelector('.register__form')

elUserRegister.addEventListener('submit',(e)=>{
    e.preventDefault()
    console.log(e.target.name.value);
    console.log(e.target.birthday.value);
    console.log(e.target.timezone.value);
    fetch(`${API__URL}/users`,{
        method: 'POST',
        headers: {
        'Content-type': 'application/json', // qysi formatta yuborish
        'Accept': 'application/json', // qysi formatta uni qabul qilib olishi
        'Access-Control-Allow-Origin': '*' // ruxsat berish hammaga
        },
        body:JSON.stringify({name: e.target.name.value, birthday: e.target.birthday.value,timezone: e.target.timezone.value})
    })
    .then((res)=> res.json())
    .then((data)=> console.log(data))
})