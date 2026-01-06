// const monthlyData = {
//   labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
//   datasets: [
//     {
//       label: "Expenses",
//       data: [500, 400, 600, 300, 450, 700, 650, 500],
//       backgroundColor: "rgba(220, 38, 38, 0.7)", // red
//       borderColor: "rgba(220, 38, 38, 1)",
//       borderWidth: 1
//     },
//     {
//       label: "Income",
//       data: [1000, 900, 1200, 800, 950, 1100, 1000, 1050],
//       backgroundColor: "rgba(22, 163, 74, 0.7)", // green
//       borderColor: "rgba(22, 163, 74, 1)",
//       borderWidth: 1
//     },
//     {
//       label: "Data",
//       data: [1000, 900, 1200, 800, 950, 1100, 1000, 1050],
//       backgroundColor: "rgba(22, 163, 74, 0.7)", // green
//       borderColor: "rgba(22, 163, 74, 1)",
//       borderWidth: 1
//     }
//   ]
// };


const ctx = document.getElementById('monthlyChart').getContext('2d');

// const monthlyChart = new Chart(ctx, {
//   type: 'bar',
//   data: monthlyData,
//   options: {
//     responsive: true,
//     plugins: {
//       legend: { position: 'top' },
//       title: { display: true, text: 'Monthly Income & Expense Trend' }
//     },
//     scales: {
//       y: { beginAtZero: true }
//     }
//   }
// });
