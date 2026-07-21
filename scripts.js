//Capture form register
const form_register = document.getElementById('form_register')

form_register.addEventListener('submit', async function(event){

    event.preventDefault();

    const data_register = new FormData(form_register)
    const object_data = Object.fromEntries(data_register)
    const urlApiRegister = "http://127.0.0.1:8000/register";

    try {
        const response_register = await fetch(urlApiRegister, {
            method:'POST',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify(object_data)
        });
    
        if (response_register.ok) {
            const result_register = await response_register.json();
            alert('Register succesfull')
            console.log('Server response:', result_register)

            form_register.reset();
        } else {
            console.error('Server response', response_register.status)
            alert('The registration could not be completed.')
        }
    } catch (error) {
        console.error('Network Error:', error);
        alert('Unable to connect to the server.');
    }
});
//Capture form login
const form_login = document.getElementById('form_login')

form_login.addEventListener('submit', async function(event){
    
    event.preventDefault();

    const data_login = new FormData(form_login)
    
    const urlApiLogin = "http://127.0.0.1:8000/login";

    try {
        const response_login = await fetch(urlApiLogin, {
            method: 'POST',
            body: data_login
        });

        if (response_login.ok) {
            const result_login = await response_login.json();
            alert('You signed in')
            console.log('Server response:', result_login)

            form_login.reset();
        } else {
            console.error('Server Error:', response_login.status);
            alert('Non-existent or incorrect username or password.');
        }
    } catch (error) {
        console.error('Network Error:', error);
        alert('Unable to connect to the server.');
    }
});