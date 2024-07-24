
// Add event listeners to each input field
document.addEventListener("DOMContentLoaded", function() {
    const inputFields = document.querySelectorAll("input");

    inputFields.forEach((input) => {
        let isFocused = false;
        let isHovered = false;

        const updateBoxShadow = () => {
            const color = window.getComputedStyle(input).borderColor;
            if (isFocused || isHovered) {
                input.style.boxShadow = `0 0 clamp(20px, 5vw, 35px) ${color}`;
            } else {
                input.style.boxShadow = 'none';
            }
            input.style.transition = 'box-shadow 0.3s ease-in-out';
        };

        input.addEventListener('focus', () => {
            isFocused = true;
            updateBoxShadow();
        });

        input.addEventListener('blur', () => {
            isFocused = false;
            updateBoxShadow();
        });

        input.addEventListener("mouseenter", () => {
            isHovered = true;
            updateBoxShadow();
        });

        input.addEventListener("mouseleave", () => {
            isHovered = false;
            updateBoxShadow();
        });
    });

    // add event listeners to submit buttons
    const submitButtons = document.getElementsByName("button");

    submitButtons.forEach((submitButton) => {
        submitButton.addEventListener("mouseenter", function() {
            const borderColor = window.getComputedStyle(submitButton).borderColor;
            submitButton.style.boxShadow = `0 0 clamp(20px, 6vw, 40px) ${borderColor}`;
            submitButton.style.backgroundColor = lightenColor(borderColor, 0.9);
            submitButton.style.color = borderColor;
        });

        submitButton.addEventListener("mouseleave", function() {
            submitButton.style.boxShadow = "none";
            submitButton.style.backgroundColor = "white"; // Reset background color
            submitButton.style.color = "black"; // Reset text color
        });
    });
});

// Function to lighten a color
function lightenColor(color, factor) {
    // Parse the color string to get RGB values
    const rgbValues = color.match(/\d+/g).map(Number);
    
    // Calculate the new lightened RGB values
    const lightenedValues = rgbValues.map(value => Math.min(value + Math.floor((255 - value) * factor), 255));
    
    // Return the new color as a string
    return `rgb(${lightenedValues.join(", ")})`;
}
