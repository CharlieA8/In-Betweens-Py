function updateCountdown() {
    const now = moment();
    const estNow = now.tz('America/New_York');

    // Find the next Sunday at midnight
    let nextSunday = estNow.clone().endOf('week').add(1, 'seconds');

    // If today is already Sunday, move to the next one
    if (estNow.day() === 0 && estNow.hour() === 0 && estNow.minute() === 0) {
        nextSunday.add(7, 'days');
    }

    const duration = moment.duration(nextSunday.diff(estNow));

    const days = Math.floor(duration.asDays());
    const hours = duration.hours();
    const minutes = duration.minutes();
    const seconds = duration.seconds();

    const countdownElement = document.getElementById('countdown');
    countdownElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

setInterval(updateCountdown, 1000);
updateCountdown();
