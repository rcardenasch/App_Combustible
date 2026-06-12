document.addEventListener("DOMContentLoaded", function () {

    let carrito = [];
    let productosCache = [];
    let proveedoresCache = [];

    // =========================
    // 🔍 BUSCAR PRODUCTO
    // =========================
    function buscarProducto(valor) {

        if (!valor) return;

        fetch(`/api/producto?q=${valor}`)
            .then(res => res.json())
            .then(lista => {

                if (!lista || lista.length === 0) {
                    alert("Producto no encontrado");
                    return;
                }

                agregarAlCarrito(lista[0]);
            });
    }

    // =========================
    // 🛒 CARRITO
    // =========================
    function agregarAlCarrito(prod) {

        let existente = carrito.find(p => p.id == prod.id);

        if (existente) {
            existente.cantidad += 1;
        } else {
            carrito.push({
                id: prod.id,
                nombre: prod.nombre,
                precio: prod.precio, // 🔥 precio compra editable
                cantidad: 1
            });
        }

        render();
    }

    function render() {

        let html = "";
        let total = 0;

        carrito.forEach((p, i) => {

            let subtotal = p.precio * p.cantidad;
            total += subtotal;

            html += `
            <tr>
                <td>
                    ${p.nombre}
                    <input type="hidden" name="producto_id" value="${p.id}">
                </td>

                <td>
                    <input type="number" step="0.01" value="${p.precio}"
                        onchange="cambiarPrecio(${i}, this.value)">
                    <input type="hidden" name="precio" value="${p.precio}">
                </td>

                <td>
                    <input type="number" value="${p.cantidad}" min="1"
                        onchange="cambiarCantidad(${i}, this.value)">
                    <input type="hidden" name="cantidad" value="${p.cantidad}">
                </td>

                <td>${subtotal.toFixed(2)}</td>

                <td>
                    <button type="button" class="btn btn-danger btn-sm"
                        onclick="eliminar(${i})">
                        🗑
                    </button>
                </td>
            </tr>`;
        });

        document.getElementById("lista").innerHTML = html;
        document.getElementById("total").innerText = total.toFixed(2);
    }

    // =========================
    // ✏️ EDITAR
    // =========================
    window.cambiarCantidad = function (index, valor) {
        carrito[index].cantidad = parseFloat(valor);
        render();
    };

    window.cambiarPrecio = function (index, valor) {
        carrito[index].precio = parseFloat(valor);
        render();
    };

    window.eliminar = function (index) {
        carrito.splice(index, 1);
        render();
    };

    // =========================
    // ⌨️ BUSCADOR ENTER
    // =========================
    let inputBuscar = document.getElementById("buscarProducto");

    if (inputBuscar) {
        inputBuscar.addEventListener("keyup", function (e) {
            if (e.key === "Enter") {
                buscarProducto(this.value);
                this.value = "";
            }
        });
    }

    // =========================
    // 🏭 PROVEEDORES
    // =========================
    let inputProveedor = document.getElementById("buscarProveedorModal");

    if (inputProveedor) {
        inputProveedor.addEventListener("keyup", function () {

            let q = this.value;
            if (q.length < 2) return;

            fetch(`/api/proveedores?q=${q}`)
                .then(res => res.json())
                .then(data => {

                    proveedoresCache = data;

                    let html = "<ul class='list-group'>";

                    data.forEach((p, i) => {
                        html += `
                        <li class="list-group-item d-flex justify-content-between"
                            onclick="seleccionarProveedor(${i})">
                            ${p.nombre}
                            <span>✔</span>
                        </li>`;
                    });

                    html += "</ul>";

                    document.getElementById("resultadosProveedores").innerHTML = html;
                });
        });
    }

    window.seleccionarProveedor = function (index) {

        let p = proveedoresCache[index];

        document.getElementById("proveedor_id").value = p.id;
        document.getElementById("proveedorSeleccionado").innerHTML =
            `<b>${p.nombre}</b>`;

        bootstrap.Modal.getInstance(document.getElementById("modalProveedor")).hide();
    };

    // =========================
    // 📦 PRODUCTOS MODAL
    // =========================
    let inputProducto = document.getElementById("buscarProductoModal");

    if (inputProducto) {
        inputProducto.addEventListener("keyup", function () {

            let q = this.value;
            if (q.length < 2) return;

            fetch(`/api/producto?q=${q}`)
                .then(res => res.json())
                .then(data => {

                    productosCache = data;

                    let html = "<ul class='list-group'>";

                    data.forEach((p, i) => {
                        html += `
                        <li class="list-group-item d-flex justify-content-between"
                            onclick="agregarDesdeModal(${i})">
                            ${p.nombre} - ${p.precio}
                            <span>➕</span>
                        </li>`;
                    });

                    html += "</ul>";

                    document.getElementById("resultadosProductos").innerHTML = html;
                });
        });
    }

    window.agregarDesdeModal = function (index) {
        agregarAlCarrito(productosCache[index]);

        bootstrap.Modal.getInstance(
            document.getElementById("modalProducto")
        ).hide();
    };

    // =========================
    // ✅ VALIDACIÓN
    // =========================
    let form = document.querySelector("form");

    if (form) {
        form.addEventListener("submit", function (e) {

            let proveedor = document.getElementById("proveedor_id").value;

            if (!proveedor) {
                e.preventDefault();
                alert("Seleccione proveedor");
                return;
            }

            if (carrito.length === 0) {
                e.preventDefault();
                alert("Agregue productos");
                return;
            }
        });
    }

});

/* Anti doble click*/
let form = document.getElementById("formCompra");

if (form) {
    form.addEventListener("submit", function () {

        let btn = document.getElementById("btnGuardar");

        btn.disabled = true;
        btn.innerHTML = "Guardando...";
    });
}