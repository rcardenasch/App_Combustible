$(document).ready(function () {

    // =========================
    // MODAL ELIMINAR
    // =========================
    const modalHTML = `
    <div class="modal fade" id="confirmDeleteModal" tabindex="-1">

        <div class="modal-dialog modal-dialog-centered">

            <div class="modal-content border-0 shadow-lg">

                <div class="modal-header bg-light">

                    <h5 class="modal-title">
                        <i class="bi bi-exclamation-triangle text-danger me-2"></i>
                        Confirmar eliminación
                    </h5>

                    <button type="button"
                            class="btn-close"
                            data-bs-dismiss="modal"></button>

                </div>

                <div class="modal-body">
                    ¿Desea eliminar este proyecto?
                </div>

                <div class="modal-footer border-0 bg-light">

                    <button type="button"
                            class="btn btn-outline-secondary"
                            data-bs-dismiss="modal">

                        Cancelar
                    </button>

                    <button type="button"
                            class="btn btn-danger"
                            id="confirmDeleteButton">

                        Eliminar
                    </button>

                </div>

            </div>

        </div>

    </div>`;

    document.body.insertAdjacentHTML("beforeend", modalHTML);

    // =========================
    // DATATABLE
    // =========================
    if ($(".datatable").length) {

        $(".datatable").DataTable({
            pageLength: 8,
            responsive: true,
            language: {
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                emptyTable: "No hay proyectos registrados",
                paginate: {
                    previous: "Anterior",
                    next: "Siguiente"
                }
            }
        });

    }

    // =========================
    // ELIMINAR
    // =========================
    window.confirmarEliminacion = function(form) {

        const modalElement = document.getElementById("confirmDeleteModal");

        const modal = new bootstrap.Modal(modalElement);

        const confirmBtn = document.getElementById("confirmDeleteButton");

        confirmBtn.innerHTML = "Eliminar";
        confirmBtn.disabled = false;

        confirmBtn.onclick = () => {

            confirmBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                Eliminando...
            `;

            confirmBtn.disabled = true;

            form.submit();
        };

        modal.show();
    };

});