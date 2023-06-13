const elFormEdit = document.querySelector('.formEdit')
const userid = 1

elFormEdit.addEventListener('submit', (e)=>{
    e.preventDefault()
    console.log(e.target.username.value);
    console.log(e.target.timezone.value);
    console.log(e.target.job.value);
    console.log(e.target.company.value);


    fetch(`${API__REGISTER}/${userid}`, {
        method: 'PUT',
        headers: {
          'Content-type': 'application/json', // qysi formatta yuborish
          'Accept': 'application/json', // qysi formatta uni qabul qilib olishi
          'Access-Control-Allow-Origin': '*' // ruxsat berish hammaga
        },
        body: JSON.stringify({
            name: e.target.username.value,
            birthday: e.target.birthday.value,
            timezone: e.target.timezone.value,
            job: e.target.job.value,
            company: e.target.company.value,
        })
      })
        .then((res) => res.json())
        .then((data) => console.table(data))
    }
)