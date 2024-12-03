
function updatePlacesList(event, target){
    let listInput = document.getElementById("placesList")
    let places = []
    if (target.value != ""){
        fetch(`${HOST_API}/variable-expenses/places/?where=${target.value}`)
        .then(res => {
            if (res.ok){
                return res.json()
            }
        })
        .then(data => {
            data.items.forEach(item => {
                places.push(`<option value='${item}'>`)
            });
            listInput.innerHTML = places.toString().replaceAll(",", "")
        })
    }
}

function updateDescriptionsList(event, target){
    let listInput = document.getElementById("descriptionsList")
    let descriptions = []
    if (target.value != ""){
        fetch(`${HOST_API}/variable-expenses/descriptions/?where=${target.value}`)
        .then(res => {
            if (res.ok){
                return res.json()
            }
        })
        .then(data => {
            data.items.forEach(item => {
                descriptions.push(`<option value='${item}'>`)
            });
            listInput.innerHTML = descriptions.toString().replaceAll(",", "")
        })
    }
}