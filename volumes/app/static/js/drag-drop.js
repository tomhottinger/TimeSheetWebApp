// Drag and Drop functionality for ticket sorting - FIXED VERSION



const DragDropModule = {

    draggedElement: null,

    draggedIndex: -1,

    

    init: function() {

        console.log('DragDropModule: Initializing...');

        this.setupDragAndDrop();

        console.log('DragDropModule: Initialization complete');

    },

    

    setupDragAndDrop: function() {

        const ticketsGrid = document.querySelector('.tickets-grid');

        if (!ticketsGrid) {

            console.log('DragDropModule: No tickets-grid found');

            return;

        }

        

        // Get all draggable ticket buttons (those with data-ticket-id)

        const ticketButtons = this.getDraggableButtons();

        console.log(`DragDropModule: Found ${ticketButtons.length} draggable tickets`);

        

        ticketButtons.forEach((button, index) => {

            console.log(`DragDropModule: Setting up ticket ${index}:`, button.dataset.ticketId);

            

            // Make the entire button draggable

            button.draggable = true;

            

            // Add all drag event listeners to the button itself

            button.addEventListener('dragstart', this.handleDragStart.bind(this));

            button.addEventListener('dragend', this.handleDragEnd.bind(this));

            button.addEventListener('dragover', this.handleDragOver.bind(this));

            button.addEventListener('drop', this.handleDrop.bind(this));

            button.addEventListener('dragenter', this.handleDragEnter.bind(this));

            button.addEventListener('dragleave', this.handleDragLeave.bind(this));

            

            // Prevent link navigation during drag

            const link = button.querySelector('a');

            if (link) {

                link.addEventListener('dragstart', (e) => {

                    e.preventDefault();

                });

            }

        });

    },

    

    getDraggableButtons: function() {

        // Get all ticket buttons with data-ticket-id (exclude stop and add buttons)

        return Array.from(document.querySelectorAll('.ticket-btn[data-ticket-id]'));

    },

    

    handleDragStart: function(e) {

        this.draggedElement = e.currentTarget;

        const buttons = this.getDraggableButtons();

        this.draggedIndex = buttons.indexOf(this.draggedElement);

        

        console.log('DragDropModule: Drag start', this.draggedElement.dataset.ticketId, 'at index', this.draggedIndex);

        

        // Visual feedback

        this.draggedElement.style.opacity = '0.4';

        this.draggedElement.classList.add('dragging');

        

        // Set drag data

        e.dataTransfer.effectAllowed = 'move';

        e.dataTransfer.setData('text/plain', this.draggedElement.dataset.ticketId);

        

        // Prevent link from activating

        const link = this.draggedElement.querySelector('a');

        if (link) {

            link.style.pointerEvents = 'none';

        }

    },

    

    handleDragEnd: function(e) {

        console.log('DragDropModule: Drag end');

        

        // Reset visual feedback

        e.currentTarget.style.opacity = '';

        e.currentTarget.classList.remove('dragging');

        

        // Clear all drop indicators

        this.clearDropIndicators();

        

        // Restore link functionality

        const link = e.currentTarget.querySelector('a');

        if (link) {

            link.style.pointerEvents = '';

        }

        

        // Reset state

        this.draggedElement = null;

        this.draggedIndex = -1;

    },

    

    handleDragOver: function(e) {

        // Necessary to allow dropping

        e.preventDefault();

        e.dataTransfer.dropEffect = 'move';

        return false;

    },

    

    handleDragEnter: function(e) {

        const target = e.currentTarget;

        

        // Don't show indicator when hovering over self

        if (target === this.draggedElement) {

            return;

        }

        

        // Clear previous indicators

        this.clearDropIndicators();

        

        // Add visual indicator

        target.style.borderLeft = '4px solid #0969da';

        target.style.marginLeft = '-2px';

        

        console.log('DragDropModule: Drag enter target:', target.dataset.ticketId);

    },

    

    handleDragLeave: function(e) {

        // Only clear if we're leaving the button entirely, not just entering a child

        const target = e.currentTarget;

        const relatedTarget = e.relatedTarget;

        

        // Check if we're moving to a child element

        if (relatedTarget && target.contains(relatedTarget)) {

            return;

        }

        

        target.style.borderLeft = '';

        target.style.marginLeft = '';

    },

    

    handleDrop: function(e) {

        e.preventDefault();

        e.stopPropagation();

        

        const dropTarget = e.currentTarget;

        

        // Don't do anything if dropping on self

        if (dropTarget === this.draggedElement) {

            return false;

        }

        

        const buttons = this.getDraggableButtons();

        const dropTargetIndex = buttons.indexOf(dropTarget);

        

        console.log('DragDropModule: Drop - moving from index', this.draggedIndex, 'to', dropTargetIndex);

        

        if (this.draggedIndex !== -1 && dropTargetIndex !== -1) {

            this.moveTicketButton(this.draggedIndex, dropTargetIndex);

            this.saveOrder();

        }

        

        return false;

    },

    

    clearDropIndicators: function() {

        document.querySelectorAll('.ticket-btn[data-ticket-id]').forEach(btn => {

            btn.style.borderLeft = '';

            btn.style.marginLeft = '';

        });

    },

    

    moveTicketButton: function(fromIndex, toIndex) {

        const buttons = this.getDraggableButtons();

        const draggedButton = buttons[fromIndex];

        const targetButton = buttons[toIndex];

        

        if (!draggedButton || !targetButton) {

            console.error('DragDropModule: Invalid button indices');

            return;

        }

        

        const parent = draggedButton.parentNode;

        

        console.log('DragDropModule: Moving button in DOM...');

        

        // Insert at new position

        if (fromIndex < toIndex) {

            // Moving forward - insert after target

            parent.insertBefore(draggedButton, targetButton.nextSibling);

        } else {

            // Moving backward - insert before target

            parent.insertBefore(draggedButton, targetButton);

        }

        

        console.log('DragDropModule: Button moved successfully');

    },

    

    getCurrentOrder: function() {

        const buttons = this.getDraggableButtons();

        const order = buttons.map(btn => btn.dataset.ticketId);

        console.log('DragDropModule: Current order:', order);

        return order;

    },

    

    saveOrder: function() {

        const newOrder = this.getCurrentOrder();

        

        console.log('DragDropModule: Saving order:', newOrder);

        

        fetch('/save_ticket_order', {

            method: 'POST',

            headers: {

                'Content-Type': 'application/json',

            },

            body: JSON.stringify({

                ticket_order: newOrder

            })

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                console.log('DragDropModule: Order saved successfully');

            } else {

                console.error('DragDropModule: Failed to save order:', data.error);

                alert('Fehler beim Speichern der Reihenfolge');

                window.location.reload();

            }

        })

        .catch(error => {

            console.error('DragDropModule: Error saving order:', error);

            alert('Fehler beim Speichern der Reihenfolge');

            window.location.reload();

        });

    }

};
