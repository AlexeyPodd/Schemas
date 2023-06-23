// Script for sending create data set request to server, and tracking it generating status

$(document).on('submit', '#post-form', function(event) {
    event.preventDefault();
    const dataSetRow = createNewDataSetRow();

    $.ajax({
        type: 'POST',
        url: dataGeneratingUrl,
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            schema: schemaSlug,
            rows: $('#rows-amount').val(),
        },
        beforeSend: function() {
            insertIntoHTMLNewDataSetRow(dataSetRow);
        },
        success: function(response) {
            updateDataSetStatus(dataSetRow, response.file_generated, response.data_set_id);
        },
    })
})

function updateDataSetStatus(row, generated, dataSetId) {
    // Adding download link
    if (generated) {
        const downloadLink = document.createElement('a');
        downloadLink.href = `${downloadUrl}?data_set=${dataSetId}`;
        downloadLink.textContent = 'Download';
        downloadLink.setAttribute('class', 'link-primary link-underline-opacity-0');

        const cellDownload = row.querySelector('td:last-child');
        cellDownload.appendChild(downloadLink);
    }

    // Updating status
    let status = document.createElement('span');
    if (generated) {
        status.setAttribute('class', 'badge text-bg-success');
        status.textContent = 'Ready';
    } else {
        status.setAttribute('class', 'badge text-bg-danger');
        status.textContent = 'Failed';
    }

    const cellStatus = row.querySelector('td:nth-child(3)');
    cellStatus.innerHTML = '';
    cellStatus.appendChild(status);
}

function createNewDataSetRow() {
    const dataSetRow = document.createElement('tr');

    const rowStart = document.createElement('th');
    rowStart.textContent = document.querySelectorAll('th.data-set-row').length + 1;
    rowStart.setAttribute('scope', 'row');
    rowStart.setAttribute('class', 'data-set-row');


    const cellDate = document.createElement('td');
    cellDate.textContent = getTodayDate();

    const cellStatus = document.createElement('td');
    const status = document.createElement('span');
    status.setAttribute('class', 'badge text-bg-secondary');
    status.textContent = 'Processing';
    cellStatus.appendChild(status);

    const cellDownload = document.createElement('td');

    dataSetRow.appendChild(rowStart);
    dataSetRow.appendChild(cellDate);
    dataSetRow.appendChild(cellStatus);
    dataSetRow.appendChild(cellDownload);

    return dataSetRow;
}

function insertIntoHTMLNewDataSetRow(block) {
    const tableBody = document.getElementById('data-sets-table-body');
    tableBody.appendChild(block);
}

function getTodayDate() {
    const currentDate = new Date();

    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0');
    const day = String(currentDate.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}