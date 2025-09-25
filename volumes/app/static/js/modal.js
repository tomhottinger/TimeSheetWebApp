// Modal functionality module

const ModalModule = {

    init: function() {

        this.setupEventListeners();

    },

    

    setupEventListeners: function() {

        // Close modal with Escape key

        document.addEventListener('keydown', function(event) {

            if (event.key === 'Escape') {

                closeTicketModal();

            }

        });

    }

};



// Modal functionality

function openAddTicketModal() {

    const modal = document.getElementById('ticketModal');

    const form = document.getElementById('ticketForm');

    const title = document.getElementById('modalTitle');

    const submitBtn = document.getElementById('submitBtn');

    const ticketIdField = document.getElementById('ticketId');

    

    // Reset for add mode

    form.action = '/add_ticket';

    title.textContent = 'Neues Zeitkonto erstellen';

    submitBtn.textContent = 'Erstellen';

    ticketIdField.value = '';

    

    // Reset form

    form.reset();

    

    // Reset color selection

    document.querySelectorAll('.preset-color').forEach(el => {

        el.classList.remove('selected');

    });

    document.querySelector('.preset-color[style*="#656d76"]').classList.add('selected');

    document.querySelector('input[name="color"]').value = '#656d76';

    

    modal.style.display = 'block';

    document.getElementById('modal-name').focus();

}



function openEditTicketModal(ticketId) {

    const modal = document.getElementById('ticketModal');

    const form = document.getElementById('ticketForm');

    const title = document.getElementById('modalTitle');

    const submitBtn = document.getElementById('submitBtn');

    const ticketIdField = document.getElementById('ticketId');

    

    // Set to edit mode

    form.action = '/update_ticket';

    title.textContent = 'Zeitkonto bearbeiten';

    submitBtn.textContent = 'Speichern';

    ticketIdField.value = ticketId;

    

    // Fetch ticket data

    fetch(`/get_ticket/${ticketId}`)

        .then(response => response.json())

        .then(data => {

            if (data.error) {

                alert('Fehler: ' + data.error);

                return;

            }

            

            // Fill form with ticket data

            document.getElementById('modal-name').value = data.name;

            document.getElementById('modal-jira').value = data.jira_ticket || '';

            document.getElementById('modal-matrix').value = data.matrix_ticket || '';

            

            // Set color

            document.querySelectorAll('.preset-color').forEach(el => {

                el.classList.remove('selected');

            });

            

            const colorInput = document.querySelector('input[name="color"]');

            colorInput.value = data.color;

            

            // Find matching preset color or mark as custom

            const matchingPreset = document.querySelector(`.preset-color[style*="${data.color}"]`);

            if (matchingPreset) {

                matchingPreset.classList.add('selected');

            }

            

            modal.style.display = 'block';

            document.getElementById('modal-name').focus();

        })

        .catch(error => {

            console.error('Error:', error);

            alert('Fehler beim Laden der Ticket-Daten');

        });

}



function closeTicketModal() {

    document.getElementById('ticketModal').style.display = 'none';

}



function closeModalOnOutsideClick(event) {

    if (event.target.id === 'ticketModal') {

        closeTicketModal();

    }

}



function selectModalColor(color) {

    // Remove selected class from all preset colors

    document.querySelectorAll('.preset-color').forEach(el => {

        el.classList.remove('selected');

    });

    

    // Add selected class to clicked color

    event.target.classList.add('selected');

    

    // Set the color input value

    document.querySelector('input[name="color"]').value = color;

}
