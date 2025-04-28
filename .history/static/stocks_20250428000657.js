/*
Stocks Module (Chart.js Integration)
1. Fetches recent stock data from Flask backend (/stocks_data)
2. Dynamically creates a Chart.js line graph for each stock symbol
3. Displays stock closing prices for the last 5 days
4. Handles cases where no data is available (displays placeholders)
5. Charts are styled for dark backgrounds(white text, aqua line colors)
*/

//store chart.js in list by each stock symbol(ex. NVDA, INTL, etc)
const charts = {};

const createChart = (symbol, labels, prices) => {
  //create new container div for each chart
  const container = document.createElement('div');
  container.className = "chart-container";

  //create canvas elemtn inside the container
  const canvas = document.createElement('canvas');
  container.appendChild(canvas);

  //attach container to charts div
  document.getElementById('charts').appendChild(container);

  //get 2d drawing context
  const ctx = canvas.getContext('2d');

  //create new chart.js line chart - line charts best for stocks over 5 days
  charts[symbol] = new Chart(ctx, {
    type: 'line',
    data: {
      //fallback label if none detected
      labels: labels.length ? labels : ["No Data"],
      datasets: [{
        label: `${symbol} Close Price`,
        //fallback data if none deteected
        data: prices.length ? prices : [0],
        //teal border
        borderColor: 'rgba(75, 192, 192, 1)',
        //light teal fill line
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        //smooth curves
        tension: 0.4,
        //small dots on each data point
        pointRadius: 3,
      }]
    },
    options: {
      responsive: true,
      animation: false,
      maintainAspectRatio: false,
      plugins: {
        //title for each graph
        title: {
          display: true,
          text: `${symbol}`,
          color: 'white',
          font: {
            size: 20
          }
        },
        legend: {
          display: false
        }
      },
      //format x and y axis
      scales: {
        x: {
          type: 'category',
          ticks: {
            color: 'white',
            font: {
              size: 12
            }
          }
        },
        y: {
          beginAtZero: false,
          ticks: {
            //format y axis labels as currency($)
            callback: function(value) {
              return `$${value.toFixed(2)}`;
            },
            color: 'white',
            font: {
              size: 12
            }
          }
        }
      }
    }
  });
};

(async () => {
  try {
    //fetch all stock data from backend
    const res = await fetch('/stocks_data');
    const allData = await res.json();

    //create chart for each stock
    for (let symbol in allData) {
      const stock = allData[symbol];

      
      createChart(symbol, stock.labels || [], stock.prices || []);
    }
  } catch (err) {
    //catch and log any errors during fetching or rendreing
    console.error('Error:', err);
  }
})();