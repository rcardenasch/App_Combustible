/* ----------------------------------------------------------
   SISTEMA — JS GLOBAL
----------------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {

    // Sidebar Toggle





    const btnToggle = document.getElementById("btnToggleSidebar");
    const sidebar = document.querySelector(".sidebar");
    const content = document.querySelector(".content");

    // Verificar el estado del sidebar desde el localStorage al cargar la página

    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
        content.classList.add('collapsed');
    }
    // Función para alternar el menú lateral
    function toggleSidebar() {
        // Toggles la clase 'collapsed' en el sidebar y el contenido
        const sidebar = document.getElementById('sidebar');
        const content = document.getElementById('content');

        sidebar.classList.toggle('collapsed');
        content.classList.toggle('collapsed');

        // Asegurarse de que el estado del menú lateral se mantenga al recargar la página
        const sidebarCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebarCollapsed);
    }


    if (btnToggle) {
        btnToggle.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            content.classList.toggle("collapsed");
        });
    }

    // Auto-cerrar alertas
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(a => a.remove());
        }, 3500);
    }

    // ===============================
    // 🌙 DARK MODE PRO (UNIFICADO)
    // ===============================
    const darkBtn = document.getElementById("btnDarkMode");

    function aplicarModoOscuro(activo) {
        const icon = darkBtn?.querySelector("i");

        if (activo) {
            document.body.classList.add("dark-mode");
            if (icon) icon.className = "bi bi-sun-fill";
        } else {
            document.body.classList.remove("dark-mode");
            if (icon) icon.className = "bi bi-moon-fill";
        }
    }

    // Toggle
    if (darkBtn) {
        darkBtn.addEventListener("click", () => {
            const activo = !document.body.classList.contains("dark-mode");

            aplicarModoOscuro(activo);
            localStorage.setItem("darkMode", activo);
        });
    }

    // Cargar estado al iniciar
    const estadoGuardado = localStorage.getItem("darkMode") === "true";
    aplicarModoOscuro(estadoGuardado);

    // Funcionalidad para mostrar notificaciones dinámicas
    function showNotification(type, message) {
        const notification = document.createElement("div");
        notification.classList.add("notification", `notification-${type}`);
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add("fade");
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    // Ejemplo de uso de notificación (puedes personalizar el tipo y mensaje)
    showNotification("success", "¡Operación completada exitosamente!");


    // Modal para eliminación con confirmación
    const modalHTML = `
        <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-labelledby="confirmDeleteModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmDeleteModalLabel">Confirmación de Eliminación</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ¿Estás seguro de que deseas eliminar este registro?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteButton">Eliminar</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modalHTML);

    // Función para mostrar el modal de confirmación de eliminación
    window.confirmarEliminacion = confirmarEliminacion;

});

/* ----------------------------------------------------------
   UTILIDADES
----------------------------------------------------------- */

// Confirmación personalizada (elimina el confirm por defecto)
function confirmarEliminacion(form) {
    const modal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
    const confirmBtn = document.getElementById("confirmDeleteButton");
    const body = document.querySelector("#confirmDeleteModal .modal-body");

    body.innerHTML = "¿Seguro que deseas eliminar este registro? Esta acción no se puede deshacer.";

    confirmBtn.onclick = () => {
        confirmBtn.innerHTML = "Eliminando...";
        confirmBtn.disabled = true;
        form.submit();
    };

    modal.show();
}

$(document).ready(function () {

    if ($(".datatable").length) {
        $(".datatable").DataTable({
            pageLength: 5,
            responsive: true,
            destroy: true, // 🔥 evita conflictos si se recarga
            language: {
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                paginate: {
                    previous: "Anterior",
                    next: "Siguiente"
                }
            }
        });
    }

});

