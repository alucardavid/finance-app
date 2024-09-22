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

function updateQueryParameters(){
    let url = window.location.href.split("?")
    limit = document.getElementById('limit')
    page = document.querySelector('li.active a')
    due_date = document.getElementById('year_month')
    where = document.getElementById('where')
    queryParameters = `?limit=${limit.value}&page=${page.innerHTML}`
    
    queryParameters += (due_date.value != '' ? `&due_date=${due_date.value}` : '')
    queryParameters += (where.value != '' ? `&where=${where.value}` : '')

    window.location.assign(url[0] + queryParameters)
}

function clearSearch(){
    document.getElementById('where').value = ""

    updateQueryParameters()
}

function updateBtnUploadCsv(event, target){
    let btnUploadCsv = document.getElementById('upload-csv')
    
    if (target.value != ''){
        btnUploadCsv.classList.remove('disabled')
    }
    else {
        btnUploadCsv.classList.add('disabled')
    }
}

function importExpenses(event, target){
    let fileInput = document.getElementById('csv-file')
    let data = new FormData()
    let file = fileInput.files[0]
    let csrfToken = getCookie('csrftoken')

    if (file != undefined){
        data.append('file', fileInput.files[0])
    
        console.log(file)
        fetch(`http://${window.location.hostname}:${window.location.port}/import-monthly-expenses/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "X-CSRFToken": csrfToken,
            },
            body: data})
            .then(res => {
                if (res.ok) {
                    return res
                }
                throw new Error('Something went wrong')
            })
            .then(res => {
                console.log(res)
            })
            .catch(err => console.log(err))

    }

}
