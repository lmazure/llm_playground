/**
 * Manages the resizable page panels.
 */
export default function manageResizablePanels() {
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
