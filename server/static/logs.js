// -----------------------------------------------------------
// LOGS MANAGEMENT
// -----------------------------------------------------------

const logPollingDuration = 1000;
let lastLogIndex = -1;

/**
 * Adds logs at the end of the logs table.
 *
 * @param {HTMLTableElement} logsTable - The logs table.
 * @param {Array} logs - An array of log objects.
 */
function addLogsRows(logsTable, logs) {
    for (let i = 0; i < logs.length; i++) {
        const log = logs[i];
        const row = document.createElement('tr');
        logsTable.appendChild(row);
        const type = document.createElement('td');
        type.textContent = log['type'];
        row.appendChild(type);
        const timestamp = document.createElement('td');
        timestamp.textContent = log['timestamp'];
        row.appendChild(timestamp);
        const message = document.createElement('td');
        message.textContent = log['message'];
        row.appendChild(message);
    }
}

/**
 * Manage logs by periodically polling the server to retrieve new logs and update the log display.
 *
 * @param {HTMLTableElement} logsTable - The logs table.
 */
function manageLogs(logsTable) {
    setInterval(function () {
        const request = new XMLHttpRequest();
        request.open('GET', '/lastLogIndex');
        request.onreadystatechange = function () {
            if ((request.readyState === 4) && (request.status === 200)) {
                let lastIndex = parseInt(request.responseText);
                if (lastIndex > lastLogIndex) {
                    const request2 = new XMLHttpRequest();
                    const firstIndex = lastLogIndex + 1;
                    request2.open('GET', '/logs?firstIndex=' + firstIndex + '&lastIndex=' + lastIndex);
                    request2.onreadystatechange = function () {
                        if ((request2.readyState === 4) && (request2.status === 200)) {
                            addLogsRows(logsTable, JSON.parse(request2.responseText));
                        }
                    };
                    request2.send();
                    lastLogIndex = lastIndex;
                }
            };
        }
        request.send();
    }, logPollingDuration);
}

/**
 * Build the logs table.
 */
export default function buildLogsTable() {
    const logsElement = document.getElementById('logs');
    const logsTable = document.createElement('table');
    const headers = ['Type', 'Timestamp', 'Message'];
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    logsTable.appendChild(headerRow);
    logsElement.appendChild(logsTable);
    manageLogs(logsTable);
}