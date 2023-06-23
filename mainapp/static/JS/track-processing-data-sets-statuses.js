// Script is tracking all data sets statuses, which was processing on moment when page was load
// Data sets, which user creates on this page, after it was load - tracks script for creating those data sets

trackProcessingStatuses();

function trackProcessingStatuses() {
    var periodicallyUpdate = setInterval(function() {
        const processingDataSetIds = getAllProcessingDataSetIds()

        if (processingDataSetIds.length === 0) {
            clearInterval(periodicallyUpdate);
        } else {
            updateProcessingStatusesFromServer(processingDataSetIds);
        }
    }, 1000)
}

function updateProcessingStatusesFromServer(processingIds) {
    $.ajax({
        type: 'GET',
        url: getGeneratingDataSetIdsUrl+`?schema=${schemaSlug}`,
        success: function(response) {
            setProcessingStatuses(processingIds, response.info);
        }
    });
}

function setProcessingStatuses(processingIds, dataSetsServerData) {
    for (let i = 0; i < processingIds.length; i++) {
        if (dataSetsServerData[processingIds[i]].finished) {
            let processingBadge = document.getElementById(`processing-data-set-badge-id-${processingIds[i]}`);
            processingBadge.removeAttribute("id");
            if (dataSetsServerData[processingIds[i]].file_generated) {
                processingBadge.setAttribute('class', "badge text-bg-success");
                processingBadge.textContent = "Ready";

                // Adding download link
                const cellDownload = processingBadge.parentNode.parentNode.querySelector('td:last-child');
                addDownloadLink(processingIds[i], cellDownload);

            } else {
                processingBadge.setAttribute('class', "badge text-bg-danger");
                processingBadge.textContent = "Failed";
            }
        }
    }
}

function getAllProcessingDataSetIds() {
    const processingBadges = document.querySelectorAll(".processing-data-set-badge");
    var dataSetIds = [];
    for (var i = 0; i < processingBadges.length; i++) {
        const element = processingBadges[i];
        const elementId = element.id;
        const dataSetId = parseInt(elementId.match(/\d+/)[0]);
        dataSetIds.push(dataSetId);
    }
    return dataSetIds
}

function addDownloadLink(dataSetId, cellDownload) {
    const downloadLink = document.createElement('a');
    downloadLink.href = `${downloadUrl}?data_set=${dataSetId}`;
    downloadLink.textContent = 'Download';
    downloadLink.setAttribute('class', 'link-primary link-underline-opacity-0');

    cellDownload.appendChild(downloadLink);
}