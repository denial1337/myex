const socket = new WebSocket('ws://127.0.0.1:8000/ws/notifications/');

// Когда соединение открыто
socket.onopen = function(e) {
    console.log('Connection established!');
};

// Когда приходит сообщение с серверной стороны
socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.type === 'update_data') {
        updateChart(message.data);
    }
};

// Функция обновления графика
function updateChart(newData) {
    chart.data.datasets[0].data = newData; // Обновляем данные
    chart.update(); // Перерисовываем график
}

