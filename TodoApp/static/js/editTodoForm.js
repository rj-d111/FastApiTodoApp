const editTodoForm = document.getElementById('editTodoForm');
if (editTodoForm) {

    editTodoForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

const form = event.target;
        const formData = new FormData(form);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            priority: parseInt(formData.get('priority')),
            complete: formData.get('complete') === 'on',
            archive: formData.get('archive') === 'on'
        };

        try {
            const response = await fetch(form.action, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                window.location.href = '/todos/todo-page'; // Redirect on success
            } else {
                const error = await response.json();
                alert('Error: ' + error.detail);
            }
        } catch (error) {
            alert('An error occurred: ' + error.message);
        }
    
    });


}

// Handle delete button with confirmation dialog
const deleteButton = document.getElementById('deleteButton');
if (deleteButton) {
    deleteButton.addEventListener('click', async function () {
        const confirmDelete = confirm('Are you sure you want to delete this todo?');
        if (confirmDelete) {
            const todoId = deleteButton.getAttribute('data-todo-id');
            try {
                const response = await fetch(`/todos/delete-todo/${todoId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include' // Include cookies in the request
                });

                if (response.ok) {
                    sessionStorage.setItem('todoDeleted', 'true');
                    window.location.href = '/todos/todo-page';
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.detail);
                }
            } catch (error) {
                alert('An error occurred: ' + error.message);
            }
        }
    });
}

