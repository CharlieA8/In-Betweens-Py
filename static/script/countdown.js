function updateCountdown() {
    const now = moment();
    const estNow = now.tz('America/New_York');

    const nextMidnight = estNow.clone().endOf('day').add(1, 'seconds');

    const duration = moment.duration(nextMidnight.diff(estNow));

    const hours = Math.floor(duration.asHours());
    const minutes = duration.minutes();
    const seconds = duration.seconds();

    const countdownElement = document.getElementById('countdown');
    countdownElement.textContent = `${hours}h ${minutes}m ${seconds}s`;
}

setInterval(updateCountdown, 1000);
updateCountdown();