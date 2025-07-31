const addTodoForm = document.getElementById('addTodoForm');

if (addTodoForm) {
    addTodoForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const form = event.target;
        const formData = new FormData(form);

        console.log(formData);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            priority: parseInt(formData.get('priority')),
            complete: false,
            archive: false
        };

        try {
            const response = await fetch(form.action, {
                method: 'POST',
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