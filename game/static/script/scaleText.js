document.addEventListener("DOMContentLoaded", function() {
    const clueBoxes = document.getElementsByClassName("clue");

    function scaleTextToFit(element) {
        let fontSize = 40; // Start with a base font size
        const maxFontSize = 100; // Maximum font size
        const minFontSize = 10; // Minimum font size

        element.style.fontSize = `${fontSize}px`;

        while (element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth) {
            if (fontSize <= minFontSize) break;
            fontSize -= 1;
            element.style.fontSize = `${fontSize}px`;
        }

        while (element.scrollHeight <= element.clientHeight && element.scrollWidth <= element.clientWidth) {
            if (fontSize >= maxFontSize) break;
            fontSize += 1;
            element.style.fontSize = `${fontSize}px`;
            if (element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth) {
                fontSize -= 1;
                element.style.fontSize = `${fontSize}px`;
                break;
            }
        }
    }

    Array.from(clueBoxes).forEach((element) => {
        scaleTextToFit(element);
    });

    // Optional: Re-scale text on window resize for all elements
    window.addEventListener("resize", () => {
        Array.from(clueBoxes).forEach((element) => {
            scaleTextToFit(element);
        });
    });

    window.addEventListener("load", () => {
        Array.from(clueBoxes).forEach((element) => {
            scaleTextToFit(element);
        });
    });
});
