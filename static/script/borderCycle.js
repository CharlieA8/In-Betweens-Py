const borderColors = [
    'rgb(178, 60, 60)', // red
    'rgb(195, 88, 195)', // purple
    'rgb(72, 72, 205)' // blue
];

let borderIndex = 1;
let otherBorderIndex = 1;

const borderElement = document.getElementById('borderCycle');
const otherBorderElement = document.getElementById('otherBorderCycle');

function cycleBorder() {
    borderElement.style.transition = 'border-color 2s, box-shadow 2s';
    borderElement.style.borderColor = borderColors[borderIndex];
    borderElement.style.boxShadow = `0 0 clamp(40px, 7vw, 60px) ${borderColors[borderIndex]}`;
    if (otherBorderElement) {
        otherBorderElement.style.transition = 'border-color 2s, box-shadow 2s';
        otherBorderElement.style.borderColor = borderColors[otherBorderIndex];
        otherBorderElement.style.boxShadow = `0 0 clamp(40px, 7vw, 60px) ${borderColors[otherBorderIndex]}`;
    }
    borderIndex = (borderIndex + 1) % borderColors.length;
    otherBorderIndex = (otherBorderIndex - 1 + borderColors.length) % borderColors.length;
    setTimeout(cycleBorder, 2000);
}

cycleBorder();
