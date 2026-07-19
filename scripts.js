//Capture form
const form_login = document.getElementById('form_login')

form_login.addEventListener('submit', async function(event){
    
    event.preventDefault();

    const data = new FormData(form_login)
    
    const urlApi = "http://127.0.0.1:8000/login";

    try {
        const response = await fetch(urlApi, {
            method: 'POST',
            body: data
        });

        if (response.ok) {
            const result = await response.json();
            alert('You signed in')
            console.log('Server response:', result)

            form_login.reset();
        } else {
            console.error('Server Error:', response.status);
            alert('There was a problem logging in.');
        }
    } catch (error) {
        console.error('Error de red:', error);
        alert('Unable to connect to the server.');
    }
});