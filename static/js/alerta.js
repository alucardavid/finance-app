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