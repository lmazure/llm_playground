
/**
 * Manages the resizable page panels.
 */
function manageResizablePanels() {
    let drag;
    let first, second;

    const separators = document.querySelectorAll('.separator');
    separators.forEach(separator => separator.addEventListener('mousedown', dragMouseDown));

    function dragMouseDown(e) {
        drag = e.clientY;
        first = e.target.previousElementSibling;
        second = e.target.nextElementSibling;
        document.onmousemove = onMouseMove;
        document.onmouseup = () => { document.onmousemove = document.onmouseup = null; }
    }

    function onMouseMove(e) {
        const delta = e.clientY - drag;
        drag = e.clientY;
        first.style.height = (first.offsetHeight + delta) + "px";
        second.style.height = (second.offsetHeight - delta) + "px";
    }
}



// -----------------------------------------------------------
// SPECIFICATION MANAGEMENT
// -----------------------------------------------------------

// Inserts a specification into a DOM node.

// Parameters:
// - node: The DOM node into which the specification will be inserted.
// - specification: The specification object that contains the title, requirements, and parts.
// - incr: The current value of the increment used to assign unique IDs to checkboxes.

// Returns:
// - The updated value of incr after inserting the specification.
function insertSpecification(node, specification, incr) {
    const h1 = document.createElement('h1');
    h1.textContent = specification['title'];
    node.appendChild(h1);
    const ul = document.createElement('ul');
    node.appendChild(ul);
    for (let i = 0; i < specification['requirements'].length; i++) {
        const requirement = specification['requirements'][i];
        const li = document.createElement('li');
        ul.appendChild(li);
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = incr;
        li.appendChild(checkbox);
        const requirement_id = document.createTextNode(requirement['id'] + " - ");
        li.appendChild(requirement_id);
        const requirement_text_lines = requirement['text'].split('\n');
        // Iterate over the lines and create text nodes and <br> elements
        for (let j = 0; j < requirement_text_lines.length; j++) {
            li.appendChild(document.createTextNode(requirement_text_lines[j]));
            if (j < (requirement_text_lines.length - 1)) {
                li.appendChild(document.createElement('br'));
            }
        }
        incr += 1;
    }
    if ('parts' in specification) {
        for (let i = 0; i < specification['parts'].length; i++) {
            const part = specification['parts'][i];
            const li = document.createElement('li');
            ul.appendChild(li);
            incr = insertSpecification(li, part, incr);
        }
    }
    return incr;
}

// Inserts a specification into the DOM.

// Parameters:
// - specification: The specification to be inserted.

// Return: None.
function insertSpecificationBlock(specification) {
    const specificationElement = document.getElementById('specification');
    const form = document.createElement('form');
    specificationElement.appendChild(form);
    insertSpecification(form, specification, 0);
    const button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.setAttribute('onclick', 'generateTestCases()');
    button.textContent = 'Generate test cases';
    form.appendChild(button);
}

function loadSpecification() {
    const request = new XMLHttpRequest();
    request.open('GET', 'http://127.0.0.1:5000/specification');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            insertSpecificationBlock(JSON.parse(request.responseText));
        }
    };
    request.send();
}

function generateTestCases() {
    const selectedItems = [];
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    for (let i = 0; i < checkboxes.length; i++) {
        selectedItems.push(checkboxes[i].id);
    }
    const request = new XMLHttpRequest();
    request.open('POST', 'http://127.0.0.1:5000/submit');
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            insertTestCasesBlock(JSON.parse(request.responseText));
        }
    };
    request.send('selectedItems=' + encodeURIComponent(JSON.stringify(selectedItems)));
}



// -----------------------------------------------------------
// MODEL PARAMETER MANAGEMENT
// -----------------------------------------------------------

function insertModelParameters(parameters) {
    const parametersElement = document.getElementById('model-parameters');
    const h1 = document.createElement('h1');
    h1.textContent = 'Model parameters';
    parametersElement.appendChild(h1);
    const form = document.createElement('form');
    form.setAttribute('id', 'model-parameters-form');
    parametersElement.appendChild(form);
    for (let i = 0; i < parameters['fields'].length; i++) {
        const field = parameters['fields'][i];
        const div = document.createElement('div');
        form.appendChild(div);
        const label = document.createElement('label');
        const title = document.createTextNode(field['title']);
        label.appendChild(title);
        div.appendChild(label);
        switch (field['type']) {
            case 'text': {
                const input = document.createElement('input');
                input.setAttribute('type', 'text');
                input.setAttribute('value', field['value']);
                input.setAttribute('name', field['key']);
                div.appendChild(input);
                break;
            }
            case 'number': {
                const input = document.createElement('input');
                input.setAttribute('type', 'number');
                input.setAttribute('value', field['value']);
                input.setAttribute('name', field['key']);
                div.appendChild(input);
                break;
            }
            case 'boolean': {
                const input = document.createElement('input');
                input.setAttribute('type', 'checkbox');
                input.checked = field['value'];
                input.setAttribute('name', field['key']);
                div.appendChild(input);
                break;
            }
            default:
                console.log('Unknown field type: ' + field['type']);
        }
    }
    const button = document.createElement('button');
    // Add an event listener to the button to handle the click event
    button.addEventListener('click', function (event) {
        event.preventDefault();
        setModelParameters();
    });
    form.appendChild(button);
    const text = document.createTextNode('Set parameters');
    button.appendChild(text);
}

function loadModelParameters() {
    const request = new XMLHttpRequest();
    request.open('GET', 'http://127.0.0.1:5000/parameters');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            insertModelParameters(JSON.parse(request.responseText));
        }
    };
    request.send();
}

function setModelParameters() {
    // Get the form element
    const form = document.getElementById('model-parameters-form');
    const payload = {};
    for (const field of form.elements) {
        if (field.name) {
            payload[field.name] = field.value;
            switch (field.type) {
                case 'text': {
                    payload[field.name] = field.value;
                    break;
                }
                case 'number': {
                    payload[field.name] = parseInt(field.value);
                    break;
                }
                case 'checkbox': {
                    payload[field.name] = field.checked;
                    break;
                }
                default:
                    console.log('Unknown field type: ' + field['type']);
                }
        }
    }
    const request = new XMLHttpRequest();
    request.open('POST', 'http://127.0.0.1:5000/parameters');
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            console.log('Parameters set successfully');
        }
    };
    request.send('parameters=' + encodeURIComponent(JSON.stringify(payload)));
}


// -----------------------------------------------------------
// TEST CASE MANAGEMENT
// -----------------------------------------------------------

// Inserts a block of test cases into the 'test-cases' element.
// 
// Parameters:
// - testCases: An array of test cases to be inserted.
// 
// Returns: None.

function insertTestCasesBlock(testCases) {
    const testCasesElement = document.getElementById('test-cases');
    const ul = document.createElement('ul');
    testCasesElement.appendChild(ul);
    for (let i = 0; i < testCases.length; i++) {
        const testCase = testCases[i];
        const li = document.createElement('li');
        ul.appendChild(li);
        const title = document.createTextNode(testCase['title']);
        li.appendChild(title);
        const br = document.createElement('br');
        li.appendChild(br);
        const table = document.createElement('table');
        table.className = "test-cases";
        li.appendChild(table);
        const headers = document.createElement('tr');
        table.appendChild(headers);
        const actionHeader = document.createElement('th');
        actionHeader.textContent = 'action';
        headers.appendChild(actionHeader);
        const resultHeader = document.createElement('th');
        resultHeader.textContent = 'result';
        headers.appendChild(resultHeader);
        const row = document.createElement('tr');
        table.appendChild(row);
        const action = document.createElement('td');
        action.textContent = testCase['action'];
        row.appendChild(action);
        const expectedResult = document.createElement('td');
        expectedResult.textContent = testCase['expected_result'];
        row.appendChild(expectedResult);
    }
}



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
        request.open('GET', 'http://127.0.0.1:5000/lastLogIndex');
        request.onreadystatechange = function () {
            if ((request.readyState === 4) && (request.status === 200)) {
                lastIndex = parseInt(request.responseText);
                if (lastIndex > lastLogIndex) {
                    const request2 = new XMLHttpRequest();
                    const firstIndex = lastLogIndex + 1;
                    request2.open('GET', 'http://127.0.0.1:5000/logs?firstIndex=' + firstIndex + '&lastIndex=' + lastIndex);
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
function buildLogsTable() {
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


// -----------------------------------------------------------
// LET'S START!
// -----------------------------------------------------------

window.addEventListener('load', function () {
    manageResizablePanels();
    loadSpecification();
    loadModelParameters();
    buildLogsTable();
});
