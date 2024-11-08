

document.addEventListener('DOMContentLoaded', async function () {
    const monthlyExpenses = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_month`);
    const balances = await fetch(`${HOST_API}/balances/`)
    const monthExpenseCategorys = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_category&where=2024-12`);
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
            text: 'Despesas Por Categoria'
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

});

