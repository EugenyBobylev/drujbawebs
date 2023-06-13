const elFeeCreation = document.querySelector('.feeCreation')

elFeeCreation.addEventListener('submit', (e)=>{
    e.preventDefault()
    const el = e.target
    const arr = []
    
    // console.log(el.type.value);
    // console.log(el.collect.value);
    // console.log(el.birthday.value);
    // console.log(el.url_card.value);
    if(el.urls_gifts.length > 1){
        for (let i = 0; i < el.urls_gifts.length; i++) {
            console.log(el.urls_gifts[i].value);
            arr.push(el.urls_gifts[i].value)
        }
    }else{
        arr.push(el.urls_gifts.value)
    }
    // console.log(el.date_type.value);
    // console.log(el.url_place.value);
    // console.log(el.time.value);
    // console.log(el.cod.value);
    fetch(`${API__feeCREATION}`,{
        method: 'POST',
        headers: {
        'Content-type': 'application/json', // qysi formatta yuborish
        'Accept': 'application/json', // qysi formatta uni qabul qilib olishi
        'Access-Control-Allow-Origin': '*' // ruxsat berish hammaga
        },
        body:JSON.stringify({
            type: el.type.value,
            collect: el.collect.value,
            birthday: el.birthday.value,
            url_card: el.url_card.value,
            date_type: el.date_type.value,
            urls_gifts: arr,
            url_place: el.url_place.value,
            time: el.time.value,
            cod: el.cod.value,
        })
    })
    .then((res)=> res.json())
    .then((data)=> console.log(data))

    console.log(arr);
})