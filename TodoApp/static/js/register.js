const registerForm = document.getElementById('registerForm');

if (registerForm){

    registerForm.addEventListener('submit', async function(event) {
       
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;
        const passwordError = document.getElementById('passwordError');

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        event.preventDefault(); // Prevent form submission for validation

        if (password !== password2) {
            event.preventDefault();
            passwordError.classList.remove('hidden');
            alert('Passwords do not match');
            return;
        } else if (password.length < 8) {
            event.preventDefault();
            passwordError.classList.remove('hidden');
            alert('Password must be at least 8 characters long');
            return;
        } else {
            passwordError.classList.add('hidden');
        }

        const payload = {
            first_name: data.first_name,
            last_name: data.last_name,
            username: data.username,
            gender: data.gender,
            country: data.country,
            email: data.email,
            password: data.password,
            birthdate: data.birthdate,
            phone_number: data.phone_number
        };

        try {
            const response = await fetch('/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/auth/login-page';
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


function isNumberKey(evt) {
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}


