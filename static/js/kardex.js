document.addEventListener("DOMContentLoaded", function () {

    const vehiculoSelect = document.getElementById("vehiculo");

    if (vehiculoSelect) {

        vehiculoSelect.addEventListener("change", function () {

            let vehiculoId = this.value;

            if (!vehiculoId) return;

            fetch(`/kardex/ultimo_horometro/${vehiculoId}`)
                .then(res => res.json())
                .then(data => {
                    const horometroInicialInput = document.getElementById("horometro_inicial");
                    const tipoOperacion = document.getElementById("tipo").value;
                    
                    // Asigna el valor al input
                    horometroInicialInput.value = data.horometro_final || 0;

                    // 🔥 CAMBIO TEMPORAL: Si es SALIDA, se permite editar SIEMPRE
                    if (tipoOperacion === "SALIDA") {
                        horometroInicialInput.removeAttribute("readonly");
                        horometroInicialInput.classList.remove("bg-secondary-subtle");
                    } else {
                        // Para OPERACION u otros, solo edita si es cero (0)
                        if (!data.horometro_final || data.horometro_final == 0) {
                            horometroInicialInput.removeAttribute("readonly");
                            horometroInicialInput.classList.remove("bg-secondary-subtle");
                        } else {
                            horometroInicialInput.setAttribute("readonly", true);
                            horometroInicialInput.classList.add("bg-secondary-subtle");
                        }
                    }
                });

        });

    }

});

$('#modalNuevo').on('hidden.bs.modal', function () {
    $("#formKardex")[0].reset();

    $("#divPrecio").removeClass("d-none");
    $("#precio_unitario").val("");

    // Restablece el input de horómetro inicial a su estado por defecto
    $("#horometro_inicial")
        .val("0.00")
        .attr("readonly", true)
        .addClass("bg-secondary-subtle");

    $("#vehiculo").prop("disabled", false);
    $("#horometro_final").prop("disabled", false);
    $("#tanque_lleno").prop("disabled", false);

    $("#alertStock").addClass("d-none");
    enviando = false;

    $("#btnGuardar")
        .prop("disabled", false)
        .html('<i class="bi bi-check-circle me-1"></i> Procesar Movimiento');
});

 $(document).ready(function () {

        // 2. Inicializar DataTable (UNA SOLA VEZ)
        if ($(".datatable").length) {
            $(".datatable").DataTable({
                pageLength: 5,
                responsive: true,
                order: [],   // respeta el orden recibido desde Flask
                language: {
                    search: "Buscar:",
                    lengthMenu: "Mostrar _MENU_ registros",
                    info: "Mostrando _START_ a _END_ de _TOTAL_",
                    emptyTable: "No hay vehículos",
                    paginate: { previous: "Anterior", next: "Siguiente" }
                }
            });
        }

        let enviando = false;

        $("#formKardex").on("submit", function (e) {

            if (enviando) {
                e.preventDefault();
                return false;
            }

            const tipo = $("#tipo").val();
            const tanque = $("#tanque option:selected");
            const cantidad = parseFloat($("#cantidad").val()) || 0;
            const stock = parseFloat(tanque.data("stock")) || 0;

            // =========================
            // VALIDACIONES
            // =========================
            if (!tipo) {
                alert("Seleccione tipo de operación");
                e.preventDefault();
                return;
            }

            if (tipo === "SALIDA") {

                if (!$("#vehiculo").val()) {
                    alert("Debe seleccionar vehículo");
                    e.preventDefault();
                    return;
                }
                    // 🔥 VALIDACIÓN NUEVA
                if (!cantidad || cantidad <= 0) {
                    alert("Debe ingresar una cantidad válida de galones");
                    e.preventDefault();
                    return;
                }

                if (cantidad > stock) {
                    $("#alertStock")
                        .removeClass("d-none")
                        .text("Stock insuficiente. Disponible: " + stock);

                    e.preventDefault();
                    return;
                }
            }

            // =========================
            // BLOQUEO SOLO SI TODO OK
            // =========================
            enviando = true;

            $("#btnGuardar")
                .prop("disabled", true)
                .html('<i class="bi bi-hourglass-split me-1"></i> Procesando...');
        });
});

$("#tipo").on("change", function () {
    toggleCamposPorTipo();
});

function toggleCamposPorTipo() {

    const tipo = $("#tipo").val();

    const vehiculo = $("#vehiculo");
    const horoFinal = $("#horometro_final");
    const tanqueLleno = $("#tanque_lleno");
    const horoInicial = $("#horometro_inicial");

    const divPrecio = $("#divPrecio");
    const precio = $("#precio_unitario");

    if (tipo === "ENTRADA") {

        vehiculo.prop("disabled", true).val("");
        horoFinal.prop("disabled", true).val("");
        tanqueLleno.prop("checked", false).prop("disabled", true);

        horoInicial
            .val("0.00")
            .prop("disabled", true)
            .addClass("bg-secondary-subtle");

        // Mostrar precio solo para entradas
        divPrecio.removeClass("d-none");
        precio.prop("required", true);

    }
    else if (tipo === "SALIDA") {

        vehiculo.prop("disabled", false);
        horoFinal.prop("disabled", false);
        tanqueLleno.prop("disabled", false);
        horoInicial.prop("disabled", false);

        // Ocultar precio
        divPrecio.addClass("d-none");
        precio.prop("required", false).val("");

    }
    else { // OPERACION

        vehiculo.prop("disabled", false);
        horoFinal.prop("disabled", false);
        tanqueLleno.prop("checked", false).prop("disabled", true);
        horoInicial.prop("disabled", false);

        // Ocultar precio
        divPrecio.addClass("d-none");
        precio.prop("required", false).val("");
    }
}
let kardexIdEliminar = null;

function confirmarAnulacion(id) {

    kardexIdEliminar = id;

    const modal = new bootstrap.Modal(
        document.getElementById("modalAnular")
    );

    modal.show();
}

function ejecutarAnulacion() {

    if (!kardexIdEliminar) return;

    const form = document.createElement("form");

    form.method = "POST";
    form.action = `/kardex/anular/${kardexIdEliminar}`;

    document.body.appendChild(form);

    form.submit();
}

$(document).ready(function () {

    toggleCamposPorTipo();

});
