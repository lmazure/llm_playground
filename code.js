
function manageResizeables()
{
  console.log("setup resizeable panels");

  var drag;
  var first, second;

  const separators = document.querySelectorAll('.separator');
  separators.forEach(separator => separator.addEventListener('mousedown', dragMouseDown));

  function dragMouseDown( e )
  {
    drag = e.clientY;
    first = e.target.previousElementSibling;
    second = e.target.nextElementSibling;
    document.onmousemove = onMouseMove;
    document.onmouseup = () => { document.onmousemove = document.onmouseup = null; }
  }

  function onMouseMove( e )
  {
    const delta = e.clientY - drag;
    drag = e.clientY;
    first.style.height = (first.offsetHeight + delta) + "px";
    second.style.height = (second.offsetHeight - delta) + "px";
  }
}
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

    function insertModelParameters(parameters) {
      const parametersElement = document.getElementById('specification');
      const h1 = document.createElement('h1');
      h1.textContent = parameters['Model parameters'];
      parametersElement.appendChild(h1);
      const ul = document.createElement('ul');
      parametersElement.appendChild(ul);
      for (let i = 0; i < parameters['fields'].length; i++) {
        const field = parameters['fields'][i];
        const li = document.createElement('li');
        ul.appendChild(li);
        const name = document.createTextNode(field['name']);
        li.appendChild(name);
      }
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


    // Add a method that is called every 500 ms and adds text at the end of the DOM.
    lastLogIndex = -1;
    function avey() {
      setInterval(function () {
        const request = new XMLHttpRequest();
        request.open('GET', 'http://127.0.0.1:5000/lastLogIndex');
        request.onreadystatechange = function () {
          if ((request.readyState === 4) && (request.status === 200)) {
            lastIndex = parseInt(request.responseText);
            console.log("lastindex: " + lastIndex + "  lastLogIndex: " + lastLogIndex);
            if (lastIndex > lastLogIndex) {
              const request2 = new XMLHttpRequest();
              const firstIndex = lastLogIndex + 1;
              request2.open('GET', 'http://127.0.0.1:5000/logs?firstIndex=' + firstIndex + '&lastIndex=' + lastIndex);
              request2.onreadystatechange = function () {
                if ((request2.readyState === 4) && (request2.status === 200)) {
                  const newElement = document.createElement('p');
                  newElement.textContent = request2.responseText;
                  document.body.appendChild(newElement);
                }
              };
              request2.send();
              lastLogIndex = lastIndex;
            }
          };
        }
        request.send();
      }, 1000);
    }

    // retrieve and display the specification when page loads
    window.addEventListener('load', function () {
      const request = new XMLHttpRequest();
      request.open('GET', 'http://127.0.0.1:5000/specification');
      request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
          insertSpecificationBlock(JSON.parse(request.responseText));
        }
      };
      request.send();
    });
      
    // retrieve and display the model parameters when page loads
    window.addEventListener('load', function () {
      const request = new XMLHttpRequest();
      request.open('GET', 'http://127.0.0.1:5000/parameters');
      request.onreadystatechange = function () {
        if ((request.readyState === 4) && (request.status === 200)) {
          insertModelParameters(JSON.parse(request.responseText));
        }
      };
      request.send();

      avey();

      manageResizeables();
    });