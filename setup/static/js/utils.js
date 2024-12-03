window.onload = function() {
    let amountInput = (document.getElementById('id_amount') == null ? document.getElementById('id_value') : document.getElementById('id_amount'));
    let valFormat = new Intl.NumberFormat('pt-BR', {
        currency: 'BRL', 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 4
    }).format(amountInput.value);
    
    amountInput.value = valFormat;
}

function checkNumberKey(event, element){
    let amountInput = document.getElementById(element.id);
    let valTmp;
    let valToFormat;
    
    console.log("Entrou");

    if(isNaN(event.key) && event.key !== 'Backspace'){
        event.preventDefault();
    }
    else {
        if(event.key == 'Backspace') {
            event.preventDefault();
            valTmp = parseInt(amountInput.value.replace(/[,.]/g, "")).toString();
            valTmp = valTmp.substring(0, valTmp.length - 1);
        }
        else {
            valTmp = Number(amountInput.value.replace(/[,.]/g, "")).toString() + event.key;
            event.preventDefault();
        }
        
        if(valTmp.length == 0){
            valToFormat = `0.00`;
        }
        else if(valTmp.length == 1){
            valToFormat = `0.0${valTmp}`;
        }
        else if(valTmp.length == 2){
            valToFormat = `0.${valTmp}`;
        }
        else if(valTmp.length == 3){
            valToFormat = `${valTmp.substring(0,1)}.${valTmp.substring(1,3)}`;
        }
        else if(valTmp.length == 4){
            valToFormat = `${valTmp.substring(0,2)}.${valTmp.substring(2,4)}`;
        }
        else {
            valToFormat = `${valTmp.substring(0,valTmp.length-2)}.${valTmp.substring(valTmp.length-2)}`;
        }
        
        let valFormat = new Intl.NumberFormat('pt-BR', {
            currency: 'BRL', 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 4
        }).format(valToFormat);
        
        amountInput.value = valFormat;
    }
}




