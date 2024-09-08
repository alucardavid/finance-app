window.onload = function() {
    let amountInput = document.getElementById('id_amount');
    let valFormat = new Intl.NumberFormat('pt-BR', {
        currency: 'BRL', 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 4
    }).format(amountInput.value);
    
    amountInput.value = valFormat;
}