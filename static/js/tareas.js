// esperar a que el documento cargue completo
document.addEventListener("DOMContentLoaded", () => {
    const saveTask = JSON.parse(localStorage.getItem("completed_tasks")) || [];
    
    // busca todos los elemento con clase task-item
    document.querySelectorAll('.task-item').forEach(task => {
        const id = task.dataset.id; 
        // si estaba marcado antes, se vuelve a marcar
        if (saveTask.includes(id)){
            task.classList.add("completed");
        }

        // evento al hacer click
        task.addEventListener('click', () => {
            // alterna añadir o quitar clase completed
            task.classList.toggle('completed');

            let update = JSON.parse(localStorage.getItem("completed_tasks")) || [];
            // añade ta tarea marcada a la lista 
            if (task.classList.contains("completed")){
                if (!update.includes(id)){
                    update.push(id)
                }
            } 
            else {
                update = update.filter(t => t !== id);
            }
            
            //actualiza la lista de marcados
            localStorage.setItem("completed_tasks", JSON.stringify(update));
        });
    });
});

// Funcion para validad que todas las tareas esten marcadas
function ValidateTask(button) {
    const card = button.closest(".card");
    const task = card.querySelectorAll(".task-item");

    let completed = 0;
    task.forEach (t => {
        if (t.classList.contains("completed")){
            completed ++;
        }
    });

    if (completed !== task.length) {
        alert("Debes completar todas las tareas para continuar");
        return false;
    }

    return true;

}

// Funcion limpiar tareas marcadas
function ClearTask(){
    localStorage.removeItem("completed_tasks");
    document.getElementById("resetForm").submit();
}