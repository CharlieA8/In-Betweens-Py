const textColors = [
    'rgb(178, 60, 60)', // red
    'rgb(195, 88, 195)', // purple
    'rgb(72, 72, 205)' // blue
];

let textIndex = 1;
const textElement = document.querySelector('[name="textCycle"]');

function cycleText() {
    textElement.style.transition = 'color 2s';
    textElement.style.color = textColors[textIndex];
    setTimeout(cycleText, 2000);
    textIndex = (textIndex + 1) % textColors.length;
}

cycleText();
