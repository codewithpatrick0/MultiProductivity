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

        if (object_data_form.priority === ""){
            delete object_data_form.priority;
        }

        if (object_data_form.id_parent_task === ""){
            delete object_data_form.id_parent_task;
        }

        if (method.toUpperCase() == 'PATCH'){
            const task_id = document.getElementById('task_id_edit').value;
            urlApi += `/${task_id}`
            delete object_data_form.task_id;
            delete object_data_form.id_category;
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
                const top_level = tasks_extracted.filter(t => t.id_parent_task === null);
                const subtasks_by_parent = {};
                tasks_extracted.filter(t => t.id_parent_task !== null).forEach(sub => {
                    if (!subtasks_by_parent[sub.id_parent_task]) subtasks_by_parent[sub.id_parent_task] = [];
                    subtasks_by_parent[sub.id_parent_task].push(sub);
                });

                const html_generated = top_level.map(task => {
                    const children = subtasks_by_parent[task.id] || [];
                    const children_html = children.map(sub =>
                        `<li style="margin-left: 20px;">↳ ${sub.title} — ${sub.status}</li>`
                    ).join('');
                    return `
                        <li><br>
                            <strong>ID Task:</strong> ${task.id} <br>
                            <strong>Title:</strong> ${task.title} <br>
                            <strong>Info:</strong> ${task.info || 'No info'} <br>
                            <strong>Status:</strong> ${task.status} </li> <br>
                        <ul>${children_html}</ul>
                    `;
                }).join('');
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

//Load cateegories
let categoriesAvailables = []

async function load_categories(
    url
){

    const categories_extracted = await call_fetch(url,
        'GET',
        null,
        {'Accept': 'Application/json'}
    )

    if (categories_extracted === null) {
        console.log('Network error loading categories')
        return false
    }

    if (categories_extracted.ok) {
        categoriesAvailables = await categories_extracted.json();
        console.log(categoriesAvailables);
        await render_categories_select();
        return true;
    } else {
        console.log('Server response: ', categories_extracted.status)
        return false;
    }
}
//Render categories
async function render_categories_select() {
    const select_categories = document.getElementById('select_category')
    const edit_categories = document.getElementById('edit_category')

    const options_generated = categoriesAvailables.map(category =>
        `
        <option value=${category.id}>${category.name}</option>
        `
    ).join('');

    select_categories.innerHTML = options_generated;
    edit_categories.innerHTML += options_generated;
    
}

//Load parent tasks
async function load_parent_task_options(url) {
    const tasks_extracted = await call_fetch(url, 'GET', null, {'Accept': 'application/json'});

    if (tasks_extracted === null || !tasks_extracted.ok) {
        console.log('Could not load parent task options');
        return;
    }

    const all_tasks = await tasks_extracted.json();
    const top_level_tasks = all_tasks.filter(task => task.id_parent_task === null);

    const select_parent = document.getElementById('select_parent_task');
    const options_generated = top_level_tasks.map(task =>
        `<option value="${task.id}">${task.title}</option>`
    ).join('');

    select_parent.innerHTML = '<option value="">None (top-level task)</option>' + options_generated;
}

//Tests JS
load_categories('http://127.0.0.1:8000/categories')
load_parent_task_options('http://127.0.0.1:8000/tasks');
create_or_edit_task('http://127.0.0.1:8000/tasks', 'form_create_task', 'POST');
create_or_edit_task('http://127.0.0.1:8000/tasks', 'form_edit_task', 'PATCH');
view_tasks('http://127.0.0.1:8000/tasks');
delete_task('http://127.0.0.1:8000/tasks');