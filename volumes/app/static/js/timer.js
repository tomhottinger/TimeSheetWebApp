// Timer functionality module
const TimerModule = {
    currentTimerInterval: null,
    
    init: function() {
        this.startTimerUpdates();
    },
    
    startTimerUpdates: function() {
        // Check if there's a current entry running
        const currentTimer = document.getElementById('currentTimer');
        if (currentTimer && currentTimer.textContent.includes('läuft')) {
            this.updateRunningTimer();
            this.currentTimerInterval = setInterval(() => {
                this.updateRunningTimer();
            }, 1000);
        }
    },
    
    updateRunningTimer: function() {
        fetch('/current_duration')
            .then(response => response.json())
            .then(data => {
                if (data.duration > 0) {
                    const timeString = formatTimeHHMM(data.duration);
                    
                    const currentTimerEl = document.getElementById('currentTimer');
                    if (currentTimerEl) {
                        currentTimerEl.innerHTML = '🟢 Timer läuft: ' + timeString;
                    }
                    
                    // Update running entries in table
                    const runningElements = document.querySelectorAll('[id^="running-"]');
                    runningElements.forEach(el => {
                        el.innerHTML = timeString;
                    });
                } else {
                    // Timer stopped, clear interval
                    if (this.currentTimerInterval) {
                        clearInterval(this.currentTimerInterval);
                        this.currentTimerInterval = null;
                    }
                }
            })
            .catch(error => console.error('Timer update error:', error));
    },
    
    stopTimer: function() {
        if (this.currentTimerInterval) {
            clearInterval(this.currentTimerInterval);
            this.currentTimerInterval = null;
        }
    }
};

// Format seconds to HH:MM
function formatTimeHHMM(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    return String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0');
}
