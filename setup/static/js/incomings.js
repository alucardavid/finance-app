function deleteExpenses(event, target){
    let expensesSelected = document.querySelectorAll('input[type="checkbox"]:checked')
    let promises = []

    expensesSelected.forEach((element) => {
        promises.push(fetch(`${HOST_API}/incomings/${element.id}/`, {method: 'DELETE'}))
    })

    if (promises.length > 0) {
        Promise.all(promises)
            .then(body => {
                window.location.reload()
            })
    }
}

function updateQueryParameters(page){
    let url = window.location.href.split("?")
    limit = document.getElementById('limit')
    page = (page === undefined ? document.querySelector('li.active a').innerHTML : page)
    where = document.getElementById('where')
    queryParameters = `?limit=${limit.value}&page=${page}`
    
    queryParameters += (where.value != '' ? `&where=${where.value}` : '')

    window.location.assign(url[0] + queryParameters)
}

function clearSearch(){
    document.getElementById('where').value = ""

    updateQueryParameters()
}