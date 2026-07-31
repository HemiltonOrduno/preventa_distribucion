/*
  RF04-06, RF11: trae el catálogo real de productos, deja capturar
  cantidades y observaciones, y envía el pedido. RF05: no se valida
  stock aquí, eso lo hace después el almacenista (RF16-21).
*/
const params = new URLSearchParams(window.location.search);
const visitaId = params.get('visita_id');

async function cargarProductos(){
    const contenedor = document.getElementById("listaProductos");
    try {
        const res = await fetch('/api/productos/productos/activos/');
        const data = await res.json();

        if (!data.productos || data.productos.length === 0){
            contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-text-muted)">No hay productos disponibles</p>`;
            return;
        }

        contenedor.innerHTML = data.productos.map(p => `
            <div class="product-item" data-codigo="${p.codigo}" data-precio="${p.precio}">
                <div>
                    <span class="product-item__name">${p.nombre}</span><br>
                    <span class="product-item__price">$${p.precio.toFixed(2)}</span>
                </div>
                <div class="qty">
                    <button type="button" class="qty__btn" onclick="cambiarCantidad(this,-1)">-</button>
                    <span class="qty__value">0</span>
                    <button type="button" class="qty__btn" onclick="cambiarCantidad(this,1)">+</button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-danger-text)">No se pudo cargar el catálogo</p>`;
    }
}

function cambiarCantidad(boton, delta){
    const contenedor = boton.closest(".qty");
    const valorSpan = contenedor.querySelector(".qty__value");
    let valor = parseInt(valorSpan.textContent, 10) + delta;
    if (valor < 0) valor = 0;
    valorSpan.textContent = valor;
}

async function confirmarPedido(){
    if (!visitaId){
        alert('No se encontró la visita, regresa a la ruta del día');
        return;
    }

    const items = document.querySelectorAll('.product-item');
    const productos = [];
    items.forEach(item => {
        const cantidad = parseInt(item.querySelector('.qty__value').textContent, 10);
        if (cantidad > 0){
            productos.push({ cod_producto: item.dataset.codigo, cantidad });
        }
    });

    if (productos.length === 0){
        alert('Selecciona al menos un producto');
        return;
    }

    const observaciones = document.getElementById("observaciones").value;

    const res = await fetch(`/api/visitas/api/visitas/${visitaId}/pedido/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productos, observaciones })
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo registrar el pedido');
        return;
    }

    window.location.href = '/api/visitas/ruta-del-dia/';
}

cargarProductos();