$(document).ready(function () {

    // =========================================
    // MODAL CONFIRMACIÓN ELIMINAR
    // =========================================
    if (!document.getElementById("confirmDeleteModal")) {

        const modalHTML = `
        <div class="modal fade"
             id="confirmDeleteModal"
             tabindex="-1"
             aria-hidden="true">

            <div class="modal-dialog modal-dialog-centered">

                <div class="modal-content border-0 shadow-lg">

                    <div class="modal-header bg-light">

                        <h5 class="modal-title fw-bold text-danger">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            Confirmar Eliminación
                        </h5>

                        <button type="button"
                                class="btn-close"
                                data-bs-dismiss="modal">
                        </button>

                    </div>

                    <div class="modal-body py-4">

                        <div class="text-center">

                            <div class="mb-3">
                                <i class="bi bi-trash3 text-danger"
                                   style="font-size: 4rem;"></i>
                            </div>

                            <h5 class="fw-bold">
                                ¿Eliminar tanque?
                            </h5>

                            <p class="text-muted mb-0">
                                Esta acción no se puede deshacer.
                            </p>

                        </div>

                    </div>

                    <div class="modal-footer border-0">

                        <button type="button"
                                class="btn btn-light px-4"
                                data-bs-dismiss="modal">

                            Cancelar
                        </button>

                        <button type="button"
                                class="btn btn-danger px-4 fw-bold"
                                id="confirmDeleteButton">

                            <i class="bi bi-trash me-1"></i>
                            Eliminar
                        </button>

                    </div>

                </div>

            </div>

        </div>`;

        document.body.insertAdjacentHTML("beforeend", modalHTML);
    }

    // =========================================
    // DATATABLE
    // =========================================
    if ($(".datatable").length) {

        $(".datatable").DataTable({

            pageLength: 5,

            responsive: true,

            order: [[0, "asc"]],

            language: {

                search: "_INPUT_",
                searchPlaceholder: "Buscar tanque...",

                lengthMenu: "Mostrar _MENU_ registros",

                info: "Mostrando _START_ a _END_ de _TOTAL_ tanques",

                emptyTable: "No hay tanques registrados",

                zeroRecords: "No se encontraron resultados",

                paginate: {
                    previous: "Anterior",
                    next: "Siguiente"
                }

            }

        });

    }

    // =========================================
    // ELIMINAR
    // =========================================
    window.confirmarEliminacion = function (form) {

        const modalElement = document.getElementById("confirmDeleteModal");

        const modal = new bootstrap.Modal(modalElement);

        const confirmBtn = document.getElementById("confirmDeleteButton");

        // reset
        confirmBtn.disabled = false;

        confirmBtn.innerHTML = `
            <i class="bi bi-trash me-1"></i>
            Eliminar
        `;

        confirmBtn.onclick = () => {

            confirmBtn.disabled = true;

            confirmBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                Eliminando...
            `;

            form.submit();
        };

        modal.show();
    };

});