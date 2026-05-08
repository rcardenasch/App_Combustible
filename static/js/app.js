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

});

