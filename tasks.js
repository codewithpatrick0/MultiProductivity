async function use_refresh_token(){
    const refreshToken = localStorage.getItem('refresh_token')
    const urlApi = 'http://127.0.0.1:8000/refresh'

    try {
        const response = await fetch(urlApi, {
            method: 'POST',
            headers: {
                'X-Refresh-Token': localStorage.getItem('refresh_token')
            }
        })
        if (response.ok) {
            const result = await response.json();
            console.log(result)
            localStorage.setItem('access_token', result.access_token)
            localStorage.setItem('refresh_token', result.refresh_token)
            return true;
        } else {
            console.log('Server response: ', response.status)
            return false;
        }
    } catch (error){
        return false;
    }
}

async function call_fetch(
    url,
    method,
    object = null,
    headers={},
    isRetry = false
){
    try{
        const upperCaseMethod = method.toUpperCase();
        const essentialHeader= {
            ...headers,
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
        
        const config = {
            method: upperCaseMethod,
            headers: essentialHeader
        }
        
        if (upperCaseMethod != "GET" && upperCaseMethod != "DELETE" && object != null){
            essentialHeader['Content-Type'] = "application/json"
            config.body = JSON.stringify(object)
        }

        const response = await fetch(url, config)

        if (response.status === 401 && !isRetry) {
            const refreshed = await use_refresh_token();
            
            if (refreshed) {
                return await call_fetch(url, method, object,headers, true)
            } else {
            alert('Session expired')
            console.log(response.status)
            }
        }
        return response
    } catch(error) {
        alert('Internal error')
        console.log('Internal error: ', error)
        return null;
    }
}

//Create or edit task
async function create_or_edit_task(
    url,
    id_form,
    method
){
    const form = document.getElementById(id_form);

    form.addEventListener('submit', async function(event){
        event.preventDefault();
        
        const data_form = new FormData(form)
        const object_data_form = Object.fromEntries(data_form)
        let urlApi = url;

        if (method.toUpperCase() == 'PATCH'){
            const task_id = document.getElementById('task_id_edit').value;
            urlApi += `/${task_id}`
            delete object_data_form.task_id;
        }
        
    
        const response = await call_fetch(urlApi,
            method,
            object_data_form, 
        )

        if (response === null){
            alert('Internal Error')
            return
        }
        const result = await response.json();
            if (response.ok){
            if (method.toUpperCase() === "POST"){
                alert('Your task created succesfull');
            }
            if (method.toUpperCase() === "PATCH"){
                alert('Task edited succesfull');
            }
            form.reset();
        } else {
            if (method.toUpperCase() === "POST"){
                alert('The task could not be created.');
            }
            if (method.toUpperCase() === "PATCH"){
                alert('The task could not be edited.');
            }
        }
        console.log('Server response:', result);

    });
};

//View tasks
async function view_tasks(url) {

    const form = document.getElementById('form_view_tasks');
    const tasks_list = document.getElementById('tasks_list');

    form.addEventListener('submit', async function(event){
        event.preventDefault();

        const response = await call_fetch(url,
            'GET', 
            null,
            {'Accept': 'application/json'}
        )
        if (response === null){
            alert('Error')
            return
        }
        if (response.ok){
            const tasks_extracted = await response.json();
            if (tasks_extracted.length > 0){
                const html_generated = tasks_extracted.map(task => 
                    `
                    <li><br>
                        <strong>ID Task:</strong> ${task.id} <br>
                        <strong>Title:</strong> ${task.title} <br>
                        <strong>Info:</strong> ${task.info || 'No info'} <br>
                        <strong>Status:</strong> ${task.status} </li> <br>
                    `
                ).join('');
                tasks_list.innerHTML = html_generated
                console.log(tasks_extracted);
            } else {
                tasks_list.innerHTML = '<p>No tasks were found.</p>';
                console.log(tasks_extracted);
            }
        } else {
            alert('Error displaying tasks')
            console.log('Server response:', response.status);
        }
    });
}

//Delete task
async function delete_task(url) {
    const form = document.getElementById('form_delete_task')
    const data_form = new FormData(form)
    
    

    form.addEventListener('submit', async function(event){
    event.preventDefault();
    
    const input_task = document.getElementById('task_id_delete')
    const task_id = input_task.value;
    let urlApi = url 
    urlApi += `/${task_id}`

    const response = await call_fetch(urlApi,
        'DELETE',
        null,
        {'Accept': 'application/json'}
    )
    if (response === null){
        alert('Error')
        return
    } 
    if (response.ok){
        alert('Task deleted sucessfull')
        console.log(response.status)

        form.reset();
    } else {
        alert('The task could not be deleted')
        console.log('Server error:', response.status)
        }
    });
}

create_or_edit_task('http://127.0.0.1:8000/tasks', 'form_create_task', 'POST');
create_or_edit_task('http://127.0.0.1:8000/tasks', 'form_edit_task', 'PATCH');
view_tasks('http://127.0.0.1:8000/tasks');
delete_task('http://127.0.0.1:8000/tasks');