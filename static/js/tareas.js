// esperar a que el documento cargue completo
document.addEventListener("DOMContentLoaded", () => {
    // busca todos los elemento con clase task-item
    document.querySelectorAll('.task-item').forEach(item => {
        // evento al hacer click
        item.addEventListener('click', () => {
            // alterna añadir o quitar clase completed
            item.classList.toggle('completed');

            if (item.classList.contains('completed')){
                fetch('')
            }
        });
    });
});