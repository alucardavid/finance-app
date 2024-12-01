
function updateDescriptionList(event, target){
    let listInput = document.getElementById("descriptionsList")
    let descriptions = []
    if (target.value != ""){
        fetch(`${HOST_API}/monthly-expenses/descriptions/?where=${target.value}`)
        .then(res => {
            if (res.ok){
                return res.json()
            }
        })
        .then(data => {
            data.items.forEach(item => {
                descriptions.push(`<option value='${item}'>`)
            });
    
            listInput.innerHTML = descriptions.toString()
    
        })
    }
}