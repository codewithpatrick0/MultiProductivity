const access_token = localStorage.getItem('access_token')

//Create task
const form_create_task = document.getElementById('form_create_task');
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
});

//View tasks
const form_view_tasks = document.getElementById('form_view_tasks');
const tasks_list = document.getElementById('tasks_list')

form_view_tasks.addEventListener('submit', async function(event){

    event.preventDefault();

    const urlApiViewTasks = 'http://127.0.0.1:8000/tasks';

    try {
        const response_view_tasks = await fetch(urlApiViewTasks, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${access_token}`,
                'Accept': 'application/json'
            }
        })
    
        if (response_view_tasks.ok){

            const tasks_extracted = await response_view_tasks.json();

            if (tasks_extracted.length > 0) {
                const html_generated = tasks_extracted.map(task =>
                    `
                    <li><br>
                        <strong>ID Task:</strong> ${task.id} <br>
                        <strong>Title:</strong> ${task.title} <br>
                        <strong>Info:</strong> ${task.info} <br>
                        <strong>Status:</strong> ${task.status} </li> <br>

                    `
                ).join('')
                tasks_list.innerHTML = html_generated
            } else {
                tasks_list.innerHTML = '<p>No tasks were found.</p>';
                console.log(tasks_extracted)
            }
        }else {
            alert('Error retrieving tasks')
            console.log('Server response:', response_view_tasks.status)
            }
        }catch(error){
            alert('Internal Error')
            console.log('Internal Error:', error)
    }
});

//Edit tasks
const form_edit_task = document.getElementById('form_edit_task')

form_edit_task.addEventListener('submit', async function(event){
    const task_id = document.getElementById('task_id_edit').value;
    event.preventDefault();

    const data_edit_task = new FormData(form_edit_task);
    const object_edit_task = Object.fromEntries(data_edit_task);
    const urlApiEditTask = `http://127.0.0.1:8000/tasks/${task_id}`;

    delete object_edit_task.task_id;

    try {
        const response_edit_task = await fetch(urlApiEditTask, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${access_token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(object_edit_task) 
        });
        if (response_edit_task.ok){
            const result_edit_task = await response_edit_task.json()
            alert('Task edited succesfull')
            console.log(result_edit_task)

            form_edit_task.reset();
        } else {
            alert('The task could not be edited.')
            console.log(response_edit_task.status)
        }
    } catch (error) {
        alert('Internal error')
        console.log('Internal error:', error)
    }
});
    
//Delete task
const form_delete_task = document.getElementById('form_delete_task')
const data_delete_task = new FormData(form_delete_task)
const input_task_id_delete = document.getElementById('task_id_delete')

form_delete_task.addEventListener('submit', async function(event){
   event.preventDefault();

   const id_delete_task = input_task_id_delete.value;

    
    const urlApiDeleteTask = `http://127.0.0.1:8000/tasks/${id_delete_task}`

    try {
        const response_delete_task = await fetch(urlApiDeleteTask, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${access_token}`,
                'Accept': 'application/json'
            }
        });

        if (response_delete_task.ok){
            alert('Task deleted sucessfull')
            console.log(response_delete_task.status)

            form_delete_task.reset();
        } else {
            alert('The task could not be deleted')
            console.log('Server error:', response_delete_task.status)
        }
    } catch (error) {
        alert('Internal Error')
        console.log('Internal Error:', error)
    }
});