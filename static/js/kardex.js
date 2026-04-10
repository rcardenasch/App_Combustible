// ========================================
// KARDEX JS
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    iniciarEscanerCodigoBarras();
    validarTransferencias();
    validarAjustes();
    activarSpinnersForms();

});


// ========================================
// ESCÁNER CÓDIGO BARRAS
// ========================================

function iniciarEscanerCodigoBarras() {

    const input = document.getElementById("codigoBarras");
    const resultado = document.getElementById("resultadoProducto");

    if (!input) return;

    input.addEventListener("keypress", async function (e) {

        if (e.key !== "Enter") return;

        e.preventDefault();

        const codigo = input.value.trim();

        if (!codigo) return;

        resultado.innerHTML = "Buscando producto...";

        try {

            const response = await fetch(`/api/kardex/producto/${codigo}`);
            const data = await response.json();

            if (!data.ok) {
                resultado.innerHTML = `
                    <div class="text-danger fw-semibold">
                        Producto no encontrado
                    </div>
                `;
                input.value = "";
                return;
            }

            resultado.innerHTML = `
                <div class="fw-bold">${data.nombre}</div>
                <div class="text-muted small">
                    ID: ${data.id}
                </div>
                <div class="small">
                    Costo Promedio: ${data.precio_compra}
                </div>
            `;

            input.value = "";

        } catch (error) {

            resultado.innerHTML = `
                <div class="text-danger">
                    Error al buscar producto
                </div>
            `;
        }
    });
}


// ========================================
// VALIDAR TRANSFERENCIAS
// ========================================

function validarTransferencias() {

    const forms = document.querySelectorAll('form[action*="transferencia"]');

    forms.forEach(form => {

        form.addEventListener("submit", function (e) {

            const origen = form.querySelector('[name="origen_id"]').value;
            const destino = form.querySelector('[name="destino_id"]').value;
            const cantidad = parseFloat(
                form.querySelector('[name="cantidad"]').value
            );

            if (origen === destino) {
                e.preventDefault();
                alert("Origen y destino no pueden ser iguales.");
                return;
            }

            if (cantidad <= 0 || isNaN(cantidad)) {
                e.preventDefault();
                alert("Cantidad inválida.");
                return;
            }

        });

    });
}


// ========================================
// VALIDAR AJUSTES INDIVIDUALES
// ========================================

function validarAjustes() {

    const forms = document.querySelectorAll('form[action*="/kardex/ajuste"]');

    forms.forEach(form => {

        form.addEventListener("submit", function (e) {

            const stock = parseFloat(
                form.querySelector('[name="nuevo_stock"]').value
            );

            if (stock < 0 || isNaN(stock)) {
                e.preventDefault();
                alert("El stock no puede ser negativo.");
                return;
            }

        });

    });

}


// ========================================
// SPINNER BOTONES SUBMIT
// ========================================

function activarSpinnersForms() {

    document.querySelectorAll("form").forEach(form => {

        form.addEventListener("submit", function () {

            const btn = form.querySelector("button[type='submit'], button:not([type])");

            if (!btn) return;

            btn.disabled = true;

            const textoOriginal = btn.innerHTML;

            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                Procesando...
            `;

            setTimeout(() => {
                btn.innerHTML = textoOriginal;
                btn.disabled = false;
            }, 5000);

        });

    });

}


// ========================================
// CONFIRM RESET STOCK
// ========================================

function confirmarReset() {
    return confirm("¿Seguro que deseas resetear todo el stock?");
}