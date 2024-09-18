function deleteExpenses(event, target){
    let expensesSelected = document.querySelectorAll('input[type="checkbox"]:checked')
    let promises = []

    expensesSelected.forEach((element) => {
        promises.push(fetch(`${HOST_API}/variable-expenses/${element.id}/`, { method: 'DELETE'}).then(res => res.json()))
    })

    if (promises.length > 0) {
        Promise.all(promises)
            .then(body => {
                window.location.reload()
            })
    }
}