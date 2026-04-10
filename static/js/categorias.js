let categoriaSeleccionada = null;
let modalActual = null;

// 👉 Selección de categoría (PADRE + HIJOS)
document.querySelectorAll(".categoria-item").forEach(item => {
    item.addEventListener("click", function (e) {

        e.stopPropagation(); // 🔥 evita que el click suba al padre

        // quitar selección previa
        document.querySelectorAll(".categoria-item").forEach(i => i.classList.remove("active"));

        // marcar seleccionado
        this.classList.add("active");

        categoriaSeleccionada = this.dataset.id;

        // activar botones
        document.getElementById("btnEditar").disabled = false;
        document.getElementById("btnEliminar").disabled = false;
    });
});

// 👉 BOTÓN EDITAR
document.getElementById("btnEditar").addEventListener("click", function () {

    if (!categoriaSeleccionada) return;

    let modalEl = document.getElementById("edit" + categoriaSeleccionada);

    if (!modalEl) {
        console.error("No existe modal para ID:", categoriaSeleccionada);
        return;
    }

    // cerrar modal anterior si existe
    if (modalActual) {
        modalActual.hide();
    }

    modalActual = new bootstrap.Modal(modalEl);
    modalActual.show();

    // 🔥 SOLUCION BLOQUEO MODAL
    modalEl.addEventListener('hidden.bs.modal', function () {
        document.body.classList.remove('modal-open');
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    });
});

// 👉 BOTÓN ELIMINAR
document.getElementById("btnEliminar").addEventListener("click", function () {

    if (!categoriaSeleccionada) return;

    let form = document.createElement("form");
    form.method = "POST";
    form.action = "/categorias/eliminar/" + categoriaSeleccionada;

    document.body.appendChild(form);

    confirmarEliminacion(form); // 👈 reemplaza confirm()
});