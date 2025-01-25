async function fetchOrderBook() {
        try {
            const response = await fetch('/api/' + ticker + '/');
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            const orderBookBody = document.getElementById('orderBookContainer');
            const data = await response.json();

            // Генерируем строки для 'ask'
            for (let i = 0; i < data.order_book.ask.price.length; i++)
            {
                let price = data.order_book.ask.price[i]
                let num = data.order_book.ask.num[i]
                const row = document.createElement('tr');
                row.classList.add('ask');
//                row.style.height = '15px';
//                row.style.width = '50px';
//                row.style.padding = '20px';
                row.innerHTML = `<td class='ob-td'>${price}</td><td class='ob-td'> ${num} </td><td class='ob-td'></td>`;
                orderBookBody.appendChild(row);
            }

            // Генерируем строки для 'bid'
            for (let i = 0; i < data.order_book.bid.price.length; i++)
            {
                let price = data.order_book.bid.price[i]
                let num = data.order_book.bid.num[i]
                const row = document.createElement('tr');
                row.classList.add('bid');
//                row.style.height = '15px';
//                row.style.width = '50px';
//                row.style.padding = '2px';
                row.innerHTML = `<td class='ob-td'> </td><td class='ob-td'> ${num} </td><td class='ob-td'>${price}</td>`;
                orderBookBody.appendChild(row);
            }
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
    }


 async function updateOrderBook() {

    const orderBookBody= document.getElementById('orderBookContainer');
    const rows = orderBookBody.getElementsByTagName('tr'); // Получаем все строки таблицы
    const response = await fetch('/api/' + ticker + '/');
    if (!response.ok) {
         throw new Error('Network response was not ok ' + response.statusText);
    }
    const data = await response.json();
    let rowIndex = 0
    for (let i = 0; i < data.order_book.ask.price.length; i++)
            {
                let price = data.order_book.ask.price[i]
                let num = data.order_book.ask.num[i]
                rows[rowIndex].cells[0].textContent = price
                rows[rowIndex].cells[1].textContent = num
                rowIndex = rowIndex + 1
            };
    for (let i = 0; i < data.order_book.bid.price.length; i++)
            {
                let price = data.order_book.bid.price[i]
                let num = data.order_book.bid.num[i]
                rows[rowIndex].cells[2].textContent = price
                rows[rowIndex].cells[1].textContent = num
                rowIndex = rowIndex + 1
            };
    };