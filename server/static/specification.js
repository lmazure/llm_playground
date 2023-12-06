import insertTestCasesBlock from './test_cases.js';

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

function generateTestCases() {
    const selectedItems = [];
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    for (let i = 0; i < checkboxes.length; i++) {
        selectedItems.push(checkboxes[i].id);
    }
    if (selectedItems.length === 0) {
        alert('Please select at least one requirement.');
    }
    const request = new XMLHttpRequest();
    request.open('POST', '/submit');
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
            insertTestCasesBlock(JSON.parse(request.responseText));
        }
    };
    request.send('selectedItems=' + encodeURIComponent(JSON.stringify(selectedItems)));
}

// Inserts a specification into the DOM.

// Parameters:
// - specification: The specification to be inserted.

// Return: None.
function insertSpecificationBlock(specification) {
    const specificationElement = document.getElementById('specification');
    const form = document.createElement('form');
    specificationElement.replaceChildren(form);
    insertSpecification(form, specification, 0);
    const button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.onclick = generateTestCases;
    button.textContent = 'Generate test cases';
    form.appendChild(button);
}


function loadSpecification(event) {

    event.preventDefault();

    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
  
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
  
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/upload', true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          insertSpecificationBlock(JSON.parse(xhr.responseText));
        } else {
          alert('File upload failed.');
        }
      };
      xhr.send(formData);
    }
}

export default function installSpecificationSelector() {
    const specificationElement = document.getElementById('specification');
    const form = document.createElement('form');
    form.setAttribute('id', 'specification-file-form');
    specificationElement.appendChild(form);
    const label = document.createElement('label');
    label.appendChild((document.createTextNode('Select specification file')));
    form.appendChild(label);
    const div = document.createElement('div');
    form.appendChild(div);
    const file = document.createElement('input');
    file.setAttribute('type', 'file');
    file.setAttribute('id', 'file-input');
    div.appendChild(file);
    // Add an event listener to the button to handle the click event
    const button = document.createElement('button');
    button.addEventListener('click', loadSpecification);
    form.appendChild(button);
    const text = document.createTextNode('Load specification');
    button.appendChild(text);
}
