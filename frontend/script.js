const endpointUrl = 'https://juan425.pythonanywhere.com/get-data';

fetch(endpointUrl)
  .then(response => response.json())
  .then(data => {
    console.log('Fetched data:', data);

    const container = document.getElementById('data-container');
    
    // Buat elemen <table>
    const table = document.createElement('table');

    // Buat <thead> dan header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    // Judul kolom
    const headers = ['Date', 'Start Time', 'End Time', 'Duration'];
    headers.forEach(headerText => {
      const th = document.createElement('th');
      th.textContent = headerText;
      headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Buat <tbody> dan isi data
    const tbody = document.createElement('tbody');
    data.forEach(item => {
      const row = document.createElement('tr');

      // Buat cell date
      const dateCell = document.createElement('td');
      dateCell.textContent = item.date;
      row.appendChild(dateCell);

      // Buat cell start_time
      const startCell = document.createElement('td');
      startCell.textContent = item.start_time;
      row.appendChild(startCell);

      // Buat cell end_time
      const endCell = document.createElement('td');
      endCell.textContent = item.end_time;
      row.appendChild(endCell);

      // Buat cell duration
      const durationCell = document.createElement('td');
      durationCell.textContent = item.duration;
      row.appendChild(durationCell);

      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(table);
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });
