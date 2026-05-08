$(document).ready(function () {
    // 1. Insertar Modal una sola vez
    const modalHTML = `
    <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirmación de Eliminación</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">¿Estás seguro de que deseas eliminar este registro?</div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-danger" id="confirmDeleteButton">Eliminar</button>
                </div>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML("beforeend", modalHTML);

    // 2. Inicializar DataTable (UNA SOLA VEZ)
    if ($(".datatable").length) {
        $(".datatable").DataTable({
            pageLength: 5,
            responsive: true,
            language: {
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                emptyTable: "No hay vehículos",
                paginate: { previous: "Anterior", next: "Siguiente" }
            }
        });
    }

    // 3. Función de eliminación
    window.confirmarEliminacion = function(form) {
        const modalElement = document.getElementById("confirmDeleteModal");
        const modal = new bootstrap.Modal(modalElement);
        const confirmBtn = document.getElementById("confirmDeleteButton");

        // Resetear estado del botón por si se canceló antes
        confirmBtn.innerHTML = "Eliminar";
        confirmBtn.disabled = false;

        confirmBtn.onclick = () => {
            confirmBtn.innerHTML = "Eliminando...";
            confirmBtn.disabled = true;
            form.submit();
        };

        modal.show();
    };
});
