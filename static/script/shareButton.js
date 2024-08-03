document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.getElementById('shareButton');
    const time = document.getElementById('time').textContent;
    
    function formatDate(date) {
        const mm = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const dd = String(date.getDate()).padStart(2, '0');
        const yy = String(date.getFullYear()).slice(-2);
        return `${mm}/${dd}/${yy}`;
    }

    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function() {
                alert('Copied to clipboard!');
            }, function(err) {
                console.error('Could not copy text: ', err);
                fallbackCopyTextToClipboard(text);
            });
        } else {
            fallbackCopyTextToClipboard(text);
        }
    }

    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        // Avoid scrolling to bottom
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = '0';
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            const successful = document.execCommand('copy');
            const msg = successful ? 'successful' : 'unsuccessful';
            alert('Copied to clipboard!');
        } catch (err) {
            console.error('Oops, unable to copy', err);
        }
        document.body.removeChild(textArea);
    }

    shareButton.addEventListener('click', function() {
        const currentDate = new Date();
        const formattedDate = formatDate(currentDate);
        const textToCopy = `🟥In+Betweens🟪${formattedDate}🟦\nTime: ${time}`;

        copyToClipboard(textToCopy);
    });
});
