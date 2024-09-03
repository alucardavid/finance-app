
function formatAmount(event, element) {
    event.preventDefault();
    let amountInput = document.getElementById(element.id);
    let valTmp = amountInput.value.replace(/[,.]/g, "").replace("^0+", "");
    let valToFormat;
    console.log(valTmp.length);

    if(valTmp.length == 0){
        valToFormat = `00.00`;
    }
    else if(valTmp.length == 1){
        valToFormat = `00.0${valTmp}`;
    }
    else if(valTmp.length == 2){
        valToFormat = `00.${valTmp}`;
    }
    else if(valTmp.length == 3){
        valToFormat = `0${valTmp.substring(0,1)}.${valTmp.substring(1,3)}`;
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

function checkNumberKey(event, element){
    if(isNaN(event.key) && event.key !== 'Backspace'){
        event.preventDefault();
    }
}




