const loginForm  = document.getElementById('loginForm');
if (loginForm) {
loginForm .addEventListener('submit', async (event) => {

    event.preventDefault(); // Prevent default form submission

    const form = event.target;
    const formData = new FormData(form);
    const payload = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
        payload.append(key, value);
    }

    try {
        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: payload.toString()
        });

        if (response.ok) {
            const data = await response.json();
            // Save the token to cookie
            document.cookie = `access_token=${data.access_token}; path=/; secure; samesite=strict`;
            window.location.href = '/todos/todo-page'; // Redirect to todo-page on success
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing your request.');
    }
});
}