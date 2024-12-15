

document.addEventListener('DOMContentLoaded', async function () {
    const monthFilter = `${new Date().getFullYear()}-${new Date().getMonth() + 1}`
    const monthlyExpenses = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_month`);
    const balances = await fetch(`${HOST_API}/balances/`)
    const monthExpenseCategorys = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_category&where=${monthFilter}`);

    const incomings = await fetch(`${HOST_API}/incomings?type_return=grouped_by_month`);
    let categories = []
    let totalExpenses = [] 
    let totalBalances = []
    let sumBalances = 0
    let expenseCategorys = []
    
    if (balances.ok){
        let data = await balances.json()

        data.forEach(item => {
            if (item.show === 'S') {
                sumBalances += item.value
            }
        })
    }

    if (monthlyExpenses.ok) {
        let expenses = await monthlyExpenses.json();
        let jsonIncomings = await incomings.json()
        let tmpBalance = sumBalances

        expenses.forEach((expense, index) => {
            
            tmpBalance -= parseInt((index > 0 ? expense.total : 0)) 
            tmpBalance += (jsonIncomings[index] != undefined ? jsonIncomings[index].total : 0)
            categories.push(expense.ano_mes)
            totalExpenses.push(expense.total)
            totalBalances.push(parseInt(tmpBalance))
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

    
    createPlacesChart(monthFilter)

});


async function createPlacesChart(monthFilter){
    const monthlyExpensePlaces = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_place&where=${monthFilter}`);
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
    const categoryChart = Highcharts.charts[1]
    let expensesCategory = []
    
    if (monthFilter == ''){
        monthFilter = `${new Date().getFullYear()}-${new Date().getMonth() + 1}`
    }

    monthlyExpenseCategory = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_category&where=${monthFilter}`);
    
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
    const placeChart = Highcharts.charts[2]
    let expensesPlace = []
    
    if (monthFilter == ''){
        monthFilter = `${new Date().getFullYear()}-${new Date().getMonth() + 1}`
    }

    monthlyExpensePlaces = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_place&where=${monthFilter}`);
    
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