// -----------------------------------------------------------
// MODEL PARAMETER MANAGEMENT
// -----------------------------------------------------------

function insertModelParameters(parameters) {

    const parametersElement = document.getElementById('model-parameters');

    const h1 = document.createElement('h1');
    h1.textContent = 'Model parameters';
    parametersElement.appendChild(h1);

    const description = document.createElement('div');
    description.setAttribute('id', 'model-description');
    description.innerHTML = parameters['html_description'];
    parametersElement.appendChild(description);

    const filler = document.createElement('div');
    filler.innerHTML = '<br><br>';
    parametersElement.appendChild(filler);

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
            case 'float': {
                const input = document.createElement('input');
                input.setAttribute('type', 'number');
                input.setAttribute('value', field['value']);
                input.setAttribute('name', field['key']);
                input.setAttribute('step', 0.01);
                if ('min' in field) {
                    input.setAttribute('min', field['min']);
                }
                if ('max' in field) {
                    input.setAttribute('max', field['max']);
                }
                div.appendChild(input);
                break;
            }
            case 'integer': {
                const input = document.createElement('input');
                input.setAttribute('type', 'number');
                input.setAttribute('value', field['value']);
                input.setAttribute('name', field['key']);
                input.setAttribute('step', 1);
                if ('min' in field) {
                    input.setAttribute('min', field['min']);
                }
                if ('max' in field) {
                    input.setAttribute('max', field['max']);
                }
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
    form.appendChild(button);
    const text = document.createTextNode('Set parameters');
    button.appendChild(text);
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        setModelParameters();
    });
}

export default function loadModelParameters() {
    const request = new XMLHttpRequest();
    request.open('GET', '/parameters');
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
    request.open('POST', '/parameters');
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            console.log('Parameters set successfully');
        }
    };
    request.send('parameters=' + encodeURIComponent(JSON.stringify(payload)));
}
