

// -----------------------------------------------------------
// TEST CASE MANAGEMENT
// -----------------------------------------------------------

// Inserts a block of test cases into the 'test-cases' element.
// 
// Parameters:
// - testCases: An array of test cases to be inserted.
// 
// Returns: None.

export default function insertTestCasesBlock(testCases) {
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