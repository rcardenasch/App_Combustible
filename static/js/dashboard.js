console.log('Dashboard JS cargado');

// =========================
// VENTAS POR DIA
// =========================

new Chart(document.getElementById('ventasChart'), {
    type: 'line',
    data: {
        labels: ventasLabels,
        datasets: [{
            label: 'Ventas',
            data: ventasData,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});


// =========================
// TOP PRODUCTOS
// =========================
new Chart(document.getElementById('productosChart'), {
    type: 'bar',
    data: {
        labels: prodLabels,
        datasets: [{
            label: 'Cantidad vendida',
            data: prodData
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});