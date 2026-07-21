//Create task
const form_create_task = document.getElementById('form_create_task');
const access_token = localStorage.getItem('access_token')
form_create_task.addEventListener('submit', async function(event){

    event.preventDefault();
    const data_new_task = new FormData(form_create_task);
    const object_new_task = Object.fromEntries(data_new_task);
    
    if (object_new_task.info.trim()==="") object_new_task.info = null;
    const urlApiCreateTask = 'http://127.0.0.1:8000/tasks';

    try {
        const response_new_task = await fetch(urlApiCreateTask, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
            body: JSON.stringify(object_new_task)
        });

        if (response_new_task.ok){
            const result_create_task = await response_new_task.json()
            alert('Your task created succesfull')
            console.log('Server response: ', result_create_task)

            form_create_task.reset();
        } else {
            alert('The task could not be created.')
            console.log('Server response:', response_new_task.status)
        }
    } catch (error) {
        alert('Internal error')
        console.log('Internal error: ', error)
    }
})