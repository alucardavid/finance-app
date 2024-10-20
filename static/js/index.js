

document.addEventListener('DOMContentLoaded', async function () {
    const monthlyExpenses = await fetch(`${HOST_API}/monthly-expenses?type_return=grouped_by_month`);
    const balances = await fetch(`${HOST_API}/balances/`)
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
        let expenses = await monthlyExpenses.json();
        let tmpBalance = sumBalances

        expenses.forEach((expense, index) => {
            
            tmpBalance -= parseInt((index > 0 ? expense.total : 0))

            categories.push(expense.ano_mes)
            totalExpenses.push(expense.total)
            totalBalances.push(parseInt(tmpBalance))
        });

    }

    const chart = Highcharts.chart('monthly-chart', {
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
});

