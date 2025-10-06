// Main JavaScript utilities



document.addEventListener('DOMContentLoaded', function() {

    // Initialize all modules

    if (typeof TimerModule !== 'undefined') {

        TimerModule.init();

    }



    if (typeof ModalModule !== 'undefined') {

        ModalModule.init();

    }



    if (typeof DateToggleModule !== 'undefined') {

        DateToggleModule.init();

    }



    if (typeof DragDropModule !== 'undefined') {

        DragDropModule.init();

    }

});



// Utility functions

function formatTime(seconds) {

    const hours = Math.floor(seconds / 3600);

    const minutes = Math.floor((seconds % 3600) / 60);

    const secs = Math.floor(seconds % 60);

    

    return String(hours).padStart(2, '0') + ':' +

           String(minutes).padStart(2, '0') + ':' +

           String(secs).padStart(2, '0');

}



// Date toggle functionality

const DateToggleModule = {

    init: function() {

        // Auto-collapse dates that aren't today

        this.setupInitialState();

    },

    

    setupInitialState: function() {

        // Already handled in template with CSS classes

    }

};



// Toggle date sections

function toggleDateSection(date) {

    const entries = document.getElementById('entries-' + date);

    const header = event.currentTarget;

    

    if (entries.style.display === 'none') {

        entries.style.display = 'block';

        header.classList.remove('collapsed');

    } else {

        entries.style.display = 'none';

        header.classList.add('collapsed');

    }

}
