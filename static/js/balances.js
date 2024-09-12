function deleteBalances(event, target){
    let expensesSelected = document.querySelectorAll('input[type="checkbox"]:checked')
    let promises = []

    expensesSelected.forEach((element) => {
        promises.push(fetch(`http://localhost:8001/balances/${element.id}/`, { method: 'DELETE'}).then())
    })

    if (promises.length > 0) {
        Promise.all(promises)
            .then(data => {
                window.location.reload()
            })
    }
}