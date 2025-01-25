function loadChart() {
    console.log('load chart init')
    const ctx = document.getElementById('chart');
    console.log(chart_price);
    console.log(ticker)
    console.log(datetime);
    chart = new Chart(ctx, {
         type: 'line',
         data: {
           labels: datetime,
           datasets: [{
             data: chart_price,
             borderWidth: 1
           }]
         },
         options: {
            animation: false,
            plugins : {
                legend: {
                    display: false,
                    },
                title: {
                    display: true,
                    text: ticker,
                    padding: {
                        top: 10,
                        bottom: 30
                    },
                    font: {
                        size: 36,
                        family: 'Helvetica Neue'
                    },
                },
            },

         responsive: false,
          scales: {
            y: {
              beginAtZero: false
            }
          }
        }
       });
    }


function updateChart(newTransactionPrice, newTransactionDateTime, chart) {
        console.log(newTransactionPrice, newTransactionDateTime)
        let data = chart.data.datasets[0].data;
        let labels = chart.data.labels;
        console.log(data)
        data.shift();
        labels.shift();

        data.push(newTransactionPrice);
        labels.push(newTransactionDateTime);

        chart.data.datasets[0].data = data
        chart.data.labels = labels

        chart.update()
    };