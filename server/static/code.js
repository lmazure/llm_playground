import manageResizablePanels from './panels.js';
import loadModelParameters from './model_parameters.js';
import loadSpecification from './specification.js';
import buildLogsTable from './logs.js';


// -----------------------------------------------------------
// LET'S START!
// -----------------------------------------------------------

window.addEventListener('load', function () {
    manageResizablePanels();
    loadSpecification();
    loadModelParameters();
    buildLogsTable();
});
