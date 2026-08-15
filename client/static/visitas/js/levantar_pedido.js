/*
  RF04-06, RF11: trae el catálogo real de productos, deja capturar
  cantidades y observaciones, y envía el pedido. RF05: no se valida
  stock aquí, eso lo hace después el almacenista (RF16-21).
*/
const params = new URLSearchParams(window.location.search);
const visitaId = params.get('visita_id');
let catalogoCompleto = [];

async function cargarProductos(){
    const contenedor = document.getElementById("listaProductos");
    try {
        const res = await fetch('/api/productos/productos/activos/');
        const data = await res.json();
        catalogoCompleto = data.productos || [];

        if (!data.productos || data.productos.length === 0){
            contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-text-muted)">No hay productos disponibles</p>`;
            return;
        }

        contenedor.innerHTML = data.productos.map(p => `
            <div class="product-item" data-codigo="${p.codigo}" data-precio="${p.precio}"
                 data-marca="${p.marca || ''}" data-peso="${p.peso || ''}"
                 data-nivel="${p.nivel_stock || ''}">
                <img class="product-item__img" src="${p.imagen}" alt="${p.nombre}"
                     onerror="this.style.visibility='hidden'">
                <div class="product-item__info">
                    <span class="product-item__name">${p.nombre}</span><br>
                    <span class="product-item__price">${p.peso ? p.peso.toFixed(0) + ' g · ' : ''}$${p.precio.toFixed(2)}</span>
                    <div class="aviso-stock" style="display:none; font-size:11px; color:#e65100; margin-top:4px;">
                        <i class='bx bx-error-circle'></i> Existencia limitada, podria surtirse la proxima semana
                    </div>
                </div>
                <div class="qty">
                    <button type="button" class="qty__btn" onclick="cambiarCantidad(this,-1)">-</button>
                    <input type="text" inputmode="numeric" class="qty__value" value="0"
                           oninput="validarCantidad(this); revisarStock(this); actualizarContador()"
                           onblur="normalizarCantidad(this)">
                    <button type="button" class="qty__btn" onclick="cambiarCantidad(this,1)">+</button>
                </div>
            </div>
        `).join('');

        llenarFiltros();

    } catch (err) {
        contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-danger-text)">No se pudo cargar el catálogo</p>`;
    }
}

const MAX_CANTIDAD = 999;

function cambiarCantidad(boton, delta){
    const input = boton.closest(".qty").querySelector(".qty__value");
    let valor = parseInt(input.value, 10);
    if (isNaN(valor)) valor = 0;
    valor += delta;
    if (valor < 0) valor = 0;
    if (valor > MAX_CANTIDAD) valor = MAX_CANTIDAD;
    input.value = valor;
    revisarStock(input);
    actualizarContador();
}

/*
  El cliente se compromete a una compra, asi que debe ver el pedido
  completo y su monto antes de que se registre. El resumen se arma con
  los precios que ya trae cada tarjeta, sin volver a consultar al
  servidor, e incluye las advertencias de existencia para que el cliente
  decida con la informacion completa.
*/
function confirmarPedido(){
    if (!visitaId){
        alert('No se encontró la visita, regresa a la ruta del día');
        return;
    }

    const items = document.querySelectorAll('.product-item');
    const lineas = [];
    const advertencias = [];
    let total = 0;

    items.forEach(item => {
        const cantidad = parseInt(item.querySelector('.qty__value').value, 10);
        if (!cantidad || cantidad <= 0) return;

        const nombre = item.querySelector('.product-item__name').textContent;
        const precio = parseFloat(item.dataset.precio) || 0;
        const peso = parseFloat(item.dataset.peso) || 0;
        const importe = cantidad * precio;
        total += importe;

        lineas.push({ nombre, cantidad, importe, precio, peso });

        const nivel = item.dataset.nivel;
        if (nivel === 'Bajo' || nivel === 'Agotado'){
            advertencias.push(nombre);
        }
    });

    if (lineas.length === 0){
        alert('Selecciona al menos un producto');
        return;
    }

    document.getElementById('resumen-lineas').innerHTML = lineas.map(l => `
        <div class="resumen-linea">
            <div>
                ${l.nombre}${l.peso ? ` <span style="color:#888;">${l.peso.toFixed(0)} g</span>` : ''}<br>
                <span class="resumen-linea__cant">${l.cantidad} pza(s) · $${l.precio.toFixed(2)} c/u</span>
            </div>
            <div>$${l.importe.toFixed(2)}</div>
        </div>
    `).join('');

    document.getElementById('resumen-total').textContent = `$${total.toFixed(2)}`;

    const cajaAviso = document.getElementById('resumen-advertencias');
    if (advertencias.length > 0){
        cajaAviso.innerHTML =
            `<b>Existencia limitada:</b> ${advertencias.join(', ')}. ` +
            `Podrian surtirse hasta la proxima semana.`;
        cajaAviso.style.display = 'block';
    } else {
        cajaAviso.style.display = 'none';
    }

    document.getElementById('modalResumen').classList.add('modal--abierto');
}

function cerrarResumen(){
    document.getElementById('modalResumen').classList.remove('modal--abierto');
}

async function enviarPedido(){
    const items = document.querySelectorAll('.product-item');
    const productos = [];

    items.forEach(item => {
        const cantidad = parseInt(item.querySelector('.qty__value').value, 10);
        if (cantidad > 0){
            productos.push({ cod_producto: item.dataset.codigo, cantidad });
        }
    });

    const observaciones = document.getElementById("observaciones").value;

    const res = await fetch(`/api/visitas/api/visitas/${visitaId}/pedido/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productos, observaciones })
    });
    const data = await res.json();

    if (!res.ok){
        cerrarResumen();
        alert(data.error || 'No se pudo registrar el pedido');
        return;
    }

    // El aviso lo muestra la pantalla de ruta del dia al volver
    window.location.href = '/api/visitas/ruta-del-dia/?completada=pedido';
}

function llenarFiltros(){
    const marcas = [...new Set(catalogoCompleto
        .map(p => p.marca)
        .filter(Boolean))].sort();

    const pesos = [...new Set(catalogoCompleto
        .map(p => p.peso)
        .filter(Boolean))].sort((a, b) => a - b);

    const selMarca = document.getElementById('filtro-marca');
    selMarca.innerHTML = '<option value="">Todas las marcas</option>' +
        marcas.map(m => `<option value="${m}">${m}</option>`).join('');

    const selPeso = document.getElementById('filtro-peso');
    selPeso.innerHTML = '<option value="">Todas las presentaciones</option>' +
        pesos.map(p => `<option value="${p}">${p} g</option>`).join('');
}

function filtrarProductos(){
    const texto = document.getElementById('buscador').value.trim().toLowerCase();
    const marca = document.getElementById('filtro-marca').value;
    const peso  = document.getElementById('filtro-peso').value;

    const items = document.querySelectorAll('.product-item');
    let visibles = 0;

    items.forEach(item => {
        const nombre = item.querySelector('.product-item__name').textContent.toLowerCase();

        const coincideTexto = !texto || nombre.includes(texto);
        const coincideMarca = !marca || item.dataset.marca === marca;
        const coincidePeso  = !peso  || item.dataset.peso === peso;

        const visible = coincideTexto && coincideMarca && coincidePeso;
        item.style.display = visible ? '' : 'none';
        if (visible) visibles++;
    });

    const contador = document.getElementById('contador-resultados');
    const hayFiltro = texto || marca || peso;

    if (!hayFiltro){
        contador.textContent = '';
    } else if (visibles === 0){
        contador.textContent = 'Ningun producto coincide con los filtros';
    } else {
        contador.textContent = `${visibles} producto(s) encontrado(s)`;
    }
}


function revisarStock(input){
    const item = input.closest('.product-item');
    const aviso = item.querySelector('.aviso-stock');
    const nivel = item.dataset.nivel;
    const cantidad = parseInt(input.value, 10) || 0;

    const escaso = nivel === 'Bajo' || nivel === 'Agotado';
    aviso.style.display = (cantidad > 0 && escaso) ? 'block' : 'none';
}

function actualizarContador(){
    const items = document.querySelectorAll('.product-item');
    let cuantos = 0;

    items.forEach(item => {
        const cantidad = parseInt(item.querySelector('.qty__value').value, 10);
        if (cantidad > 0) cuantos++;
    });

    const contador = document.getElementById('contador-carrito');
    if (contador) contador.textContent = cuantos;
}

cargarProductos();