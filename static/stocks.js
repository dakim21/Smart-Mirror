const charts = {};

const createChart = (symbol, labels, prices) => {
  const container = document.createElement('div');
  container.className = "chart-container";

  const canvas = document.createElement('canvas');
  container.appendChild(canvas);

  document.getElementById('charts').appendChild(container);

  const ctx = canvas.getContext('2d');

  charts[symbol] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ["No Data"], // ✅ Show "No Data" if labels empty
      datasets: [{
        label: `${symbol} Close Price`,
        data: prices.length ? prices : [0], // ✅ Show 0 if no real prices
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        pointRadius: 3,
      }]
    },
    options: {
      responsive: true,
      animation: false,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${symbol} (Last 5 Days)`,
          color: 'white',
          font: {
            size: 20
          }
        },
        legend: {
          display: false
        }
      },
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
    const res = await fetch('/stocks_data');
    const allData = await res.json();

    for (let symbol in allData) {
      const stock = allData[symbol];

      // 🔥 Remove skip logic: always try to create a chart
      createChart(symbol, stock.labels || [], stock.prices || []);
    }
  } catch (err) {
    console.error('Error loading stock data:', err);
  }
})();