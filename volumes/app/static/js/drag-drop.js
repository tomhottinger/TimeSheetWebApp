// Drag and Drop functionality for ticket sorting

const DragDropModule = {

    draggedElement: null,

    draggedIndex: -1,

    dropTargetIndex: -1,

    

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

        

        // Get all drag handles instead of buttons

        const dragHandles = Array.from(document.querySelectorAll('.drag-handle[data-ticket-id]'));

        console.log(`DragDropModule: Found ${dragHandles.length} drag handles`);

        

        dragHandles.forEach((handle, index) => {

            console.log(`DragDropModule: Setting up drag handle ${index}:`, handle.dataset.ticketId);

            handle.draggable = true;

            

            handle.addEventListener('dragstart', this.handleDragStart.bind(this));

            handle.addEventListener('dragover', this.handleDragOver.bind(this));

            handle.addEventListener('drop', this.handleDrop.bind(this));

            handle.addEventListener('dragend', this.handleDragEnd.bind(this));

            handle.addEventListener('dragenter', this.handleDragEnter.bind(this));

            handle.addEventListener('dragleave', this.handleDragLeave.bind(this));

        });

        

        // Also add event listeners to ticket buttons for drop zones

        const ticketButtons = this.getDraggableButtons();

        ticketButtons.forEach(button => {

            button.addEventListener('dragover', this.handleDragOver.bind(this));

            button.addEventListener('drop', this.handleDrop.bind(this));

            button.addEventListener('dragenter', this.handleDragEnter.bind(this));

            button.addEventListener('dragleave', this.handleDragLeave.bind(this));

        });

    },

    

    getDraggableButtons: function() {

        // Get all ticket buttons with data-ticket-id, excluding stop and add buttons

        const buttons = Array.from(document.querySelectorAll('.ticket-btn[data-ticket-id]'));

        console.log('DragDropModule: Found draggable buttons:', buttons.map(b => ({id: b.dataset.ticketId, element: b})));

        return buttons;

    },

    

    handleDragStart: function(e) {

        // Make sure we get the actual ticket button, not a child element

        let target = e.target;

        while (target && !target.dataset.ticketId) {

            target = target.parentElement;

        }

        

        if (!target || !target.dataset.ticketId) {

            console.error('DragDropModule: Could not find ticket button');

            return;

        }

        

        this.draggedElement = target;

        const buttons = this.getDraggableButtons();

        this.draggedIndex = buttons.indexOf(target);

        

        console.log('DragDropModule: Drag start', target.dataset.ticketId, 'at index', this.draggedIndex);

        

        target.style.opacity = '0.5';

        e.dataTransfer.effectAllowed = 'move';

        e.dataTransfer.setData('text/plain', target.dataset.ticketId);

        

        // Prevent the link from working during drag

        const link = target.querySelector('a');

        if (link) {

            link.style.pointerEvents = 'none';

        }

    },

    

    handleDragOver: function(e) {

        e.preventDefault();

        e.dataTransfer.dropEffect = 'move';

        return false;

    },

    

    handleDragEnter: function(e) {

        // Make sure we get the actual ticket button

        let target = e.target;

        while (target && !target.dataset.ticketId) {

            target = target.parentElement;

        }

        

        if (target && target.dataset.ticketId && target !== this.draggedElement) {

            // Remove previous indicators

            this.clearDropIndicators();

            

            // Add indicator to current target

            target.style.borderLeft = '3px solid #0969da';

            

            const buttons = this.getDraggableButtons();

            this.dropTargetIndex = buttons.indexOf(target);

            console.log('DragDropModule: Drag enter target index', this.dropTargetIndex, 'ticket:', target.dataset.ticketId);

        }

    },

    

    handleDragLeave: function(e) {

        if (e.target.dataset.ticketId) {

            e.target.style.borderLeft = '';

        }

    },

    

    handleDrop: function(e) {

        e.preventDefault();

        e.stopPropagation();

        

        console.log('DragDropModule: Drop - moving from index', this.draggedIndex, 'to', this.dropTargetIndex);

        

        if (this.draggedIndex !== -1 && this.dropTargetIndex !== -1 && 

            this.draggedIndex !== this.dropTargetIndex) {

            

            this.moveTicketButton(this.draggedIndex, this.dropTargetIndex);

            this.saveOrder();

        }

        

        return false;

    },

    

    handleDragEnd: function(e) {

        console.log('DragDropModule: Drag end');

        

        // Reset styles

        e.target.style.opacity = '';

        this.clearDropIndicators();

        

        // Restore link functionality

        const link = e.target.querySelector('a');

        if (link) {

            link.style.pointerEvents = '';

        }

        

        // Reset state

        this.draggedElement = null;

        this.draggedIndex = -1;

        this.dropTargetIndex = -1;

    },

    

    clearDropIndicators: function() {

        document.querySelectorAll('.ticket-btn[data-ticket-id]').forEach(btn => {

            btn.style.borderLeft = '';

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

        

        // Remove dragged element temporarily

        const nextSibling = draggedButton.nextSibling;

        draggedButton.remove();

        

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

                // Reload page on error to restore original order

                window.location.reload();

            }

        })

        .catch(error => {

            console.error('DragDropModule: Error saving order:', error);

            // Reload page on error to restore original order

            window.location.reload();

        });

    }

};
