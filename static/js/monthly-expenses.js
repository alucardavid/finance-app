function updateLimit(event, target){
    let url = window.location.href.split("?")
    let finalUrl = `${url[0]}?limit=${target.value}`
    
    if (url.length > 1) {
        queryStrings = url[1].split("&")
        queryStrings.forEach(item => {
            if (item.split("=")[0] == "page") {
                finalUrl += `&page=${item.split("=")[1]}`
            }
        });
    }

    window.location.assign(finalUrl) 
}

function deleteExpenses(event, target){
    let expensesSelected = document.querySelectorAll('input[type="checkbox"]:checked')
    let promises = []

    expensesSelected.forEach((element) => {
        promises.push(fetch(`${HOST_API}/monthly-expenses/${element.id}/`, {method: 'DELETE'}).then(res => res.json()))
    })

    if (promises.length > 0) {
        Promise.all(promises)
            .then(body => {
                window.location.reload()
            })
    }
}