APIurl = 'http://ec2-54-172-93-84.compute-1.amazonaws.com/todos'

let todoItems = [];

function renderTodo(todo) {
    const list = document.querySelector('.js-todo-list');
    const item = document.querySelector(`[data-task_id='${todo.task_id}']`);

    if (todo.isDeleted && item) {
        list.removeChild(item);
        return;
    }

    const isChecked = todo.is_done ? 'done' : '';
    const node = document.createElement("li");
    node.setAttribute('class', `todo-item ${isChecked}`);
    node.setAttribute('data-task_id', todo.task_id);
    node.setAttribute('data-is_done', todo.is_done);
    node.innerHTML = `
    <input id="${todo.task_id}" type="checkbox"/>
    <label for="${todo.task_id}" class="tick js-tick"></label>
    <div>
    <span>${todo.title}</span>
    <p>___ ${todo.description}</p>
    </div>
    <button class="delete-todo js-delete-todo">
    <svg><use href="#delete-icon"></use></svg>
    </button>
  `;

    if (item) {
        list.replaceChild(node, item);
    } else {
        list.append(node);
    }
}

function addTodo(title, desc) {
    body_ = JSON.stringify({
        'title': String(title),
        'description': String(desc),
    })

    fetch(APIurl, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: body_
    })
        .then(result => result.json().then(data => ({ status: result.status, body: data })))
        .then(res => {
            if (res.status == 201) {
                renderTodo(res.body['newly added todo']);
            }
        });
}

function toggleDone(task_id, is_done) {
    body_ = JSON.stringify({ 'is_done': String(!is_done) })

    fetch(APIurl + '/' + task_id, {
        method: 'PUT',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: body_
    })
        .then(result => result.json().then(data => ({ status: result.status, body: data })))
        .then(res => {
            if (res.status == 200) {
                renderTodo(res.body['updated todo']);
            }
        });
}

function deleteTodo(task_id) {
    fetch(APIurl + '/' + task_id, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
        .then(result => result.json().then(data => ({ status: result.status, body: data })))
        .then(res => {
            if (res.status == 200) {
                renderTodo({ task_id: task_id, isDeleted: true });
            }
        });
}

const form = document.querySelector('.js-form');
form.addEventListener('submit', event => {
    event.preventDefault();
    const titleInput = document.querySelector('.js-todo-input');
    const descInput = document.querySelector('.js-todo-details');

    const title = titleInput.value.trim().replace(/'/g, "").replace(/"/g, "");
    const desc = descInput.value.trim().replace(/'/g, "").replace(/"/g, "");
    if (title !== '') {
        addTodo(title, desc);
        titleInput.value = '';
        descInput.value = '';
        titleInput.focus();
    }
});

const list = document.querySelector('.js-todo-list');
list.addEventListener('click', event => {
    if (event.target.classList.contains('js-tick')) {
        const task_id = event.target.parentElement.dataset.task_id;
        const is_done = event.target.parentElement.dataset.is_done;
        toggleDone(task_id, Number(is_done));
    }

    if (event.target.classList.contains('js-delete-todo')) {
        const task_id = event.target.parentElement.dataset.task_id;
        deleteTodo(task_id);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    fetch(APIurl)
        .then(result => result.json().then(data => ({ status: result.status, body: data })))
        .then(res => {
            if (res.status == 200) {
                res.body.todos.forEach(t => {
                    renderTodo(t);
                });
            }
        });
});