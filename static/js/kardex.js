// ======================================================
// ESTADO GLOBAL
// ======================================================
let enviando = false;
let kardexIdEliminar = null;

// ======================================================
// INICIALIZACIÓN
// ======================================================
$(document).ready(function () {

    // --------------------------------------------------
    // 1. INICIALIZAR DATATABLE
    // --------------------------------------------------
    if (
        $(".datatable").length &&
        !$.fn.DataTable.isDataTable(".datatable")
    ) {
        $(".datatable").DataTable({
            pageLength: 10,
            responsive: true,
            order: [],
            language: {
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                emptyTable: "No hay movimientos registrados",
                zeroRecords: "No se encontraron registros",
                paginate: {
                    previous: "Anterior",
                    next: "Siguiente"
                }
            }
        });
    }

    // --------------------------------------------------
    // 2. CAMBIAR PROYECTO SIN RECARGAR LA PÁGINA
    // --------------------------------------------------
    $("#proyecto").on("change", function () {

        const proyectoId = this.value;

        if (!proyectoId) return;

        const tanqueSelect = $("#tanque");
        const vehiculoSelect = $("#vehiculo");
        const operadorSelect = $("#operador");

        tanqueSelect.prop("disabled", true);
        vehiculoSelect.prop("disabled", true);
        operadorSelect.prop("disabled", true);

        tanqueSelect.html(
            '<option value="">Cargando tanques...</option>'
        );
        vehiculoSelect.html(
            '<option value="">Cargando vehículos...</option>'
        );
        operadorSelect.html(
            '<option value="">Cargando operadores...</option>'
        );

        $("#horometro_inicial")
            .val("0.00")
            .prop("readonly", true)
            .addClass("bg-secondary-subtle");

        $("#horometro_final").val("");
        $("#alertStock").addClass("d-none").text("");

        fetch(
            `/kardex/recursos_proyecto/${encodeURIComponent(proyectoId)}`
        )
            .then(response => {
                if (!response.ok) {
                    throw new Error(
                        response.status === 403
                            ? "No tienes permiso para acceder a ese proyecto."
                            : `Error HTTP ${response.status} al cargar los recursos.`
                    );
                }

                return response.json();
            })
            .then(data => {

                // Comprobar que la respuesta tenga las tres listas
                if (
                    !Array.isArray(data.tanques) ||
                    !Array.isArray(data.vehiculos) ||
                    !Array.isArray(data.operadores)
                ) {
                    throw new Error(
                        "La respuesta del servidor no contiene las listas esperadas."
                    );
                }

                // -----------------------------
                // TANQUES
                // -----------------------------
                tanqueSelect.empty().append(
                    new Option("Seleccione Tanque", "")
                );

                data.tanques.forEach(t => {
                    const option = new Option(
                        `${t.nombre} (Disponible: ${Number(t.stock_actual || 0).toFixed(2)} Gls)`,
                        t.id
                    );

                    option.dataset.stock = t.stock_actual || 0;
                    option.dataset.proyectoId = proyectoId;

                    tanqueSelect.append(option);
                });

                // -----------------------------
                // VEHÍCULOS
                // -----------------------------
                vehiculoSelect.empty().append(
                    new Option("Seleccione Vehículo", "")
                );

                data.vehiculos.forEach(v => {
                    const option = new Option(v.nombre, v.id);
                    option.dataset.proyectoId = proyectoId;
                    vehiculoSelect.append(option);
                });

                // -----------------------------
                // OPERADORES
                // -----------------------------
                operadorSelect.empty().append(
                    new Option("Seleccione Operador", "")
                );

                data.operadores.forEach(o => {
                    const option = new Option(o.nombre, o.id);
                    option.dataset.proyectoId = proyectoId;
                    operadorSelect.append(option);
                });

                // Recursos cargados correctamente
                tanqueSelect.prop("disabled", false);
                vehiculoSelect.prop("disabled", false);
                operadorSelect.prop("disabled", false);

                // Aplicar las reglas del tipo de movimiento
                toggleCamposPorTipo();

                console.log("Proyecto seleccionado:", proyectoId);
                console.log("Tanques:", data.tanques.length);
                console.log("Vehículos:", data.vehiculos.length);
                console.log("Operadores:", data.operadores.length);

            })
            .catch(error => {

                console.error(
                    "Error al cargar recursos del proyecto:",
                    error
                );

                tanqueSelect.empty().append(
                    new Option("No se pudieron cargar los tanques", "")
                );

                vehiculoSelect.empty().append(
                    new Option("No se pudieron cargar los vehículos", "")
                );

                operadorSelect.empty().append(
                    new Option("No se pudieron cargar los operadores", "")
                );

                // Se mantienen deshabilitados para evitar
                // registrar movimientos con datos incorrectos.
                alert(error.message);
            });
    });

    // --------------------------------------------------
    // 3. CAMBIO DE VEHÍCULO: ÚLTIMO HORÓMETRO
    // --------------------------------------------------
    $("#vehiculo").on("change", function () {

        const vehiculoId = $(this).val();
        const horometroInicial = $("#horometro_inicial");
        const tipoOperacion = $("#tipo").val();

        if (!vehiculoId) {
            horometroInicial
                .val("0.00")
                .prop("readonly", true)
                .addClass("bg-secondary-subtle");

            return;
        }

        fetch(`/kardex/ultimo_horometro/${vehiculoId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("No se pudo consultar el horómetro.");
                }
                return response.json();
            })
            .then(data => {

                const horometro = parseFloat(data.horometro_final) || 0;

                horometroInicial.val(horometro.toFixed(2));

                // SALIDA: permite editar el horómetro inicial.
                if (tipoOperacion === "SALIDA") {

                    horometroInicial
                        .prop("readonly", false)
                        .removeClass("bg-secondary-subtle");

                } else if (horometro === 0) {

                    horometroInicial
                        .prop("readonly", false)
                        .removeClass("bg-secondary-subtle");

                } else {

                    horometroInicial
                        .prop("readonly", true)
                        .addClass("bg-secondary-subtle");
                }
            })
            .catch(error => {
                console.error("Error al obtener horómetro:", error);
                alert("No se pudo obtener el último horómetro del vehículo.");
            });
    });

    // --------------------------------------------------
    // 4. CAMBIO DE TIPO DE MOVIMIENTO
    // --------------------------------------------------
    $("#tipo").on("change", function () {
        toggleCamposPorTipo();
    });

    // --------------------------------------------------
    // 5. VALIDACIÓN Y ENVÍO DEL FORMULARIO
    // --------------------------------------------------
    $("#formKardex").on("submit", function (e) {

        if (enviando) {
            e.preventDefault();
            return false;
        }

        const tipo = $("#tipo").val();
        const tanque = $("#tanque option:selected");
        const cantidad = parseFloat($("#cantidad").val()) || 0;
        //const stock = parseFloat(tanque.attr("data-stock")) || 0;
        const stock = parseFloat($("#tanque option:selected").attr("data-stock")) || 0;

        // Tipo obligatorio
        if (!tipo) {
            alert("Seleccione tipo de operación.");
            e.preventDefault();
            return false;
        }

        // Tanque obligatorio
        if (!$("#tanque").val()) {
            alert("Debe seleccionar un tanque.");
            e.preventDefault();
            return false;
        }

        // Vehículo y cantidad para SALIDA
        if (tipo === "SALIDA") {

            if (!$("#vehiculo").val()) {
                alert("Debe seleccionar un vehículo.");
                e.preventDefault();
                return false;
            }

            if (cantidad <= 0) {
                alert("Debe ingresar una cantidad válida de galones.");
                e.preventDefault();
                return false;
            }

            if (cantidad > stock) {
                $("#alertStock")
                    .removeClass("d-none")
                    .text(
                        "Stock insuficiente. Disponible: " +
                        stock.toFixed(2) + " galones."
                    );

                e.preventDefault();
                return false;
            }
        }

        // Bloquear el botón solo cuando todas las validaciones pasaron.
        enviando = true;

        $("#btnGuardar")
            .prop("disabled", true)
            .html(
                '<i class="bi bi-hourglass-split me-1"></i> Procesando...'
            );
    });

    // --------------------------------------------------
    // 6. RESTABLECER MODAL AL CERRAR
    // --------------------------------------------------
    $("#modalNuevo").on("hidden.bs.modal", function () {

        const formulario = $("#formKardex")[0];

        if (formulario) {
            formulario.reset();
        }

        $("#divPrecio").removeClass("d-none");
        $("#precio_unitario").val("");

        $("#horometro_inicial")
            .val("0.00")
            .prop("readonly", true)
            .prop("disabled", false)
            .addClass("bg-secondary-subtle");

        $("#vehiculo").prop("disabled", false);
        $("#horometro_final").prop("disabled", false);
        $("#tanque_lleno").prop("disabled", false);

        $("#alertStock")
            .addClass("d-none")
            .text("");

        enviando = false;

        $("#btnGuardar")
            .prop("disabled", false)
            .html(
                '<i class="bi bi-check-circle me-1"></i> Procesar Movimiento'
            );

        toggleCamposPorTipo();
    });

    // Estado inicial
    toggleCamposPorTipo();
});


// ======================================================
// CAMPOS SEGÚN TIPO DE MOVIMIENTO
// ======================================================
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

        tanqueLleno
            .prop("checked", false)
            .prop("disabled", true);

        horoInicial
            .val("0.00")
            .prop("disabled", true)
            .prop("readonly", true)
            .addClass("bg-secondary-subtle");

        divPrecio.removeClass("d-none");
        precio.prop("required", true);

    } else if (tipo === "SALIDA") {

        vehiculo.prop("disabled", false);
        horoFinal.prop("disabled", false);
        tanqueLleno.prop("disabled", false);

        horoInicial
            .prop("disabled", false);

        divPrecio.addClass("d-none");
        precio.prop("required", false).val("");

    } else if (tipo === "OPERACION") {

        vehiculo.prop("disabled", false);
        horoFinal.prop("disabled", false);

        tanqueLleno
            .prop("checked", false)
            .prop("disabled", true);

        horoInicial
            .prop("disabled", false);

        divPrecio.addClass("d-none");
        precio.prop("required", false).val("");

    } else {

        // Sin tipo seleccionado
        vehiculo.prop("disabled", true).val("");
        horoFinal.prop("disabled", true).val("");

        tanqueLleno
            .prop("checked", false)
            .prop("disabled", true);

        divPrecio.addClass("d-none");
        precio.prop("required", false).val("");
    }
}


// ======================================================
// ANULACIÓN DE MOVIMIENTO
// ======================================================
function confirmarAnulacion(id) {

    kardexIdEliminar = id;

    const modal = new bootstrap.Modal(
        document.getElementById("modalAnular")
    );

    modal.show();
}


function ejecutarAnulacion() {

    if (!kardexIdEliminar) {
        return;
    }

    const form = document.createElement("form");

    form.method = "POST";
    form.action = `/kardex/anular/${kardexIdEliminar}`;

    document.body.appendChild(form);
    form.submit();
}


