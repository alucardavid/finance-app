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

function payExpenses(event, target){
    let expensesSelected = document.querySelectorAll('input[type="checkbox"]:checked')
    let promises = []

    expensesSelected.forEach((element) => {
        promises.push(fetch(`${HOST_API}/monthly-expenses/pay/${element.id}/`, {method: 'PUT'}))
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
    due_date = document.getElementById('year_month')
    where = document.getElementById('where')
    queryParameters = `?limit=${limit.value}&page=${page}`
    
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
    let btnUploadCsv = document.getElementById('upload-csv')
    let labelBtnUploadCsv = document.getElementById('btn-upload-csv-label')
    let spinnerLoading = document.getElementById('spinner-upload-csv')
    let data = new FormData()
    let file = fileInput.files[0]
    let csrfToken = getCookie('csrftoken')

    if (file != undefined){
        data.append('file', fileInput.files[0])
        btnUploadCsv.classList.add('disabled')
        spinnerLoading.classList.remove('d-none')
        labelBtnUploadCsv.innerText = 'Carregando'

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
                throw new Error('Something went wrong, please check the file format or items.')
            })
            .then(res => {
                window.location.reload()
            })
            .catch(err => {
                showAlert(err)
            })
            .finally(res => {
                btnUploadCsv.classList.remove('disabled')
                spinnerLoading.classList.add('d-none')
                labelBtnUploadCsv.innerText = 'Importar CSV'      
            })

    }

}

function showAlert(msg){
    let alertDiv = document.getElementById('alerta')
    let alertLabel = document.getElementById('alerta-label')

    alertLabel.innerText = msg

    alertDiv.style.display = "block"

    setTimeout(() => {
        alertDiv.style.opacity = "1"
    }, 100);
}

function closeAlert(event, target){
    let alertDiv = document.getElementById('alerta')

    alertDiv.style.opacity = "0"
    
    setTimeout(() => {
        alertDiv.style.display = "none"
    }, 600);

}

function checkDeleteBtn(event, target){
    let countCheck = document.querySelectorAll('input[type="checkbox"]:checked').length
    let deleteBtn = document.getElementById("delete-expenses")
    let payBtn = document.getElementById("pay-expenses")

    if (countCheck > 0 ){
        deleteBtn.classList.remove("disabled")
        payBtn.classList.remove("disabled")
    }
    else {
        deleteBtn.classList.add("disabled")
        payBtn.classList.add("disabled")
    }
}

function importFaturaSantander(event, target){
    let fileInput = document.getElementById('import-santander')   
    let btnUpload = document.getElementById('btn-santander-upload')
    let spinnerLoading = document.getElementById('spinner-import-santander')
    let data = new FormData()
    let file = fileInput.files[0]
    let csrfToken = getCookie('csrftoken')
    
    if (file != undefined) {
        data.append('file', fileInput.files[0])
        btnUpload.classList.add('disabled')
        spinnerLoading.classList.remove('d-none')

        fetch(`http://${window.location.hostname}:${window.location.port}/import-fatura-santander/`, {
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
                throw new Error('Something went wrong, please check the file format or items.')
            })
            .then(res => {
                window.location.reload()
            })
            .catch(err => {
                showAlert(err)
            })
            .finally(res => {
                btnUpload.classList.remove('disabled')
                spinnerLoading.classList.add('d-none')
            })
    }
     
}