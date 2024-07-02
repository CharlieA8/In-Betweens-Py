const borderColors = [
    'rgb(178, 60, 60)', // red
    'rgb(195, 88, 195)', // purple
    'rgb(72, 72, 205)' // blue
];

let borderIndex = 1;

const borderElement = document.getElementById('borderCycle');

function cycleBorder() {
    borderElement.style.transition = 'border-color 2s, box-shadow 2s';
    borderElement.style.borderColor = borderColors[borderIndex];
    borderElement.style.boxShadow = `0 0 clamp(40px, 7vw, 60px) ${borderColors[borderIndex]}`;
    borderIndex = (borderIndex + 1) % borderColors.length;
    setTimeout(cycleBorder, 2000);
}

cycleBorder();
