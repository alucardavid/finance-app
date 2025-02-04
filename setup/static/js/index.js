

document.addEventListener('DOMContentLoaded', async function () {
    const currentDate = new Date()
    let monthFilter = getYearMonthNow()
    const monthlyExpenses = await fetch(`${HOST_API}/monthly-expenses?due_date=${monthFilter}&status=Pendente&type_return=grouped_by_place`);
    let expenses = await monthlyExpenses.json()
    let filterInput = document.getElementById('month_filter')

    if (expenses.length == 0) {
        currentDate.setMonth(currentDate.getMonth() + 1)
        monthFilter = `${currentDate.getFullYear()}-${(currentDate.getUTCMonth()).toString().length == 1 ? '0' + (currentDate.getUTCMonth()) : (currentDate.getUTCMonth()) }`
    }
    
    filterInput.value = monthFilter

    createMonthlyChart()
    createCategoryChart(monthFilter)    
    createPlacesChart(monthFilter)

});

async function createMonthlyChart(){
    const monthlyExpenses = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_month`);
    const balances = await fetch(`${HOST_API}/balances/`)
    const incomings = await fetch(`${HOST_API}/incomings?type_return=grouped_by_month`);
    let categories = []
    let totalExpenses = [] 
    let totalBalances = []
    let sumBalances = 0
        
    if (balances.ok){
        let data = await balances.json()

        data.forEach(item => {
            if (item.show === 'S') {
                sumBalances += item.value
            }
        })
    }

    if (monthlyExpenses.ok) {
        let expenses = await monthlyExpenses.json()
        let jsonIncomings = await incomings.json()
        let tmpBalance = sumBalances
        let tmpTotal = 0

        expenses.forEach((expense, index) => {
            
            tmpBalance += (jsonIncomings[index] != undefined ? jsonIncomings[index].total : 0)
            tmpBalance -= parseInt((index > 0 ? tmpTotal : 0)) 
            categories.push(expense.ano_mes)
            totalExpenses.push(expense.total)
            totalBalances.push(parseInt(tmpBalance))
            tmpTotal = expense.total
        });

    }

    const monthlyChart = Highcharts.chart('monthly-chart', {
        chart: {
            type: 'line'
        },
        title: {
            text: 'Despesas Mensais x Saldos'
        },
        xAxis: {
            categories: categories,
        },
        yAxis: {
            title: {
                text: 'Valor R$'
            }
        },
        plotOptions:{
            series: {
                events: {
                    click: function(e) {
                        console.log(this)
                    }
                }
            }
        },
        series: [{
            name: 'Despesas',
            data: totalExpenses,
            color: '#FF0000'
        },{
            name: 'Saldos',
            data: totalBalances,
            color: '#42f578'
        }]
    });
}

async function createCategoryChart(monthFilter){
    const monthExpenseCategorys = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_category&due_date=${monthFilter}`);
    let expenseCategorys = []

    if (monthExpenseCategorys.ok){
        let expenses = await monthExpenseCategorys.json();

        expenses.forEach((expense) => {
            expenseCategorys.push({
                "name": expense.category,
                "y": expense.total
            })
        })
    }

    const categoryChart = Highcharts.chart('category-chart', {
        chart: {
            type: 'pie'
        },
        title: {
            text: `Despesas Por Categoria - ${monthFilter}`
        },
        plotOptions: {
            series: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: [{
                    enabled: true,
                    distance: 20
                }, {
                    enabled: true,
                    distance: -40,
                    format: '{point.percentage:.1f}%',
                    style: {
                        fontSize: '1.2em',
                        textOutline: 'none',
                        opacity: 0.7
                    },
                    filter: {
                        operator: '>',
                        property: 'percentage',
                        value: 10
                    }
                }]
            }
        },
        series: [{
            name: 'Total',
            colorByPoint: true,
            data: expenseCategorys
        }]
    });
}   

async function createPlacesChart(monthFilter){
    const monthlyExpensePlaces = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_place&due_date=${monthFilter}`);
    let expensesPlace = []

    if (monthlyExpensePlaces.ok){
        let expenses = await monthlyExpensePlaces.json();

        expenses.forEach((expense) => {
            expensesPlace.push({
                "name": expense.place,
                "y": expense.total
            })
        })
    }

    const placeChart = Highcharts.chart('place-chart', {
        chart: {
            type: 'pie'
        },
        title: {
            text: `Despesas Por Lugar - ${monthFilter}`
        },
        plotOptions: {
            series: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: [{
                    enabled: true,
                    distance: 20
                }, {
                    enabled: true,
                    distance: -40,
                    format: '{point.percentage:.1f}%',
                    style: {
                        fontSize: '1.2em',
                        textOutline: 'none',
                        opacity: 0.7
                    },
                    filter: {
                        operator: '>',
                        property: 'percentage',
                        value: 10
                    }
                }]
            }
        },
        series: [{
            name: 'Total',
            colorByPoint: true,
            data: expensesPlace
        }]
    });
}

async function updateCharts(event, target){
    let monthFilter = target.value

    updatePlaceChart(monthFilter)
    updateCategoryChart(monthFilter)

}

async function updateCategoryChart(monthFilter){
    let monthlyExpenseCategory = Object
    const categoryChart = Highcharts.charts.find((element) => element.renderTo.id == 'category-chart')
    let expensesCategory = []
    
    if (monthFilter == ''){
        monthFilter = `${new Date().getFullYear()}-${new Date().getMonth() + 1}`
    }

    monthlyExpenseCategory = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_category&due_date=${monthFilter}`);
    
    if (monthlyExpenseCategory.ok){
        let expenses = await monthlyExpenseCategory.json();

        expenses.forEach((expense) => {
            expensesCategory.push({
                "name": expense.category,
                "y": expense.total
            })
        })
    }

    categoryChart.setTitle({text: `Despesas Por Categoria - ${monthFilter}`})
    categoryChart.series[0].setData(expensesCategory)
}

async function updatePlaceChart(monthFilter){
    let monthlyExpensePlaces = Object
    const placeChart = Highcharts.charts.find((element) => element.renderTo.id == 'place-chart')
    let expensesPlace = []
    
    if (monthFilter == ''){
        monthFilter = `${new Date().getFullYear()}-${new Date().getMonth() + 1}`
    }

    monthlyExpensePlaces = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_place&due_date=${monthFilter}`);
    
    if (monthlyExpensePlaces.ok){
        let expenses = await monthlyExpensePlaces.json();

        expenses.forEach((expense) => {
            expensesPlace.push({
                "name": expense.place,
                "y": expense.total
            })
        })
    }

    placeChart.setTitle({text: `Despesas Por Lugar - ${monthFilter}`})
    placeChart.series[0].setData(expensesPlace)

}

function getYearMonthNow(){
    const currentDate = new Date()
    year = currentDate.getFullYear()
    month = currentDate.getMonth() + 1

    if (month < 10) {
        month = `0${month}`
    }

    return `${year}-${month}`

}