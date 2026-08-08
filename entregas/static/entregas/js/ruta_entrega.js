// ===== VARIABLES GLOBALES =====
const ALMACEN = { lat: 32.4700, lon: -116.9400, nombre: 'Almacén Sabritas - El Florido' };
const OSRM_URL = 'http://127.0.0.1:5000';

let mapa = null;
let rutaLayer = null;
let marcadores = {};
let paradas = [];
let paradaActual = null;
let entregaId = null;
let rutaId = null;
let tipoPagoSeleccionado = 'TP001';
let rutaIniciada = false;

// ===== INICIALIZAR MAPA =====
function inicializarMapa() {
    mapa = L.map('map', {
        center: [32.505, -117.010],
        zoom: 12
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(mapa);

    // Leaflet no detecta solo los cambios de tamaño del contenedor
    window.addEventListener('resize', () => {
        setTimeout(() => mapa.invalidateSize(), 200);
    });
    window.addEventListener('orientationchange', () => {
        setTimeout(() => mapa.invalidateSize(), 300);
    });
}

// ===== CARGAR RUTA =====
function cargarRuta() {
    fetch('/api/entregas/mi-ruta/')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                // Si no trae ruta propia, se ofrecen las entregas disponibles
                if (data.error.includes('ruta asignada')) {
                    mostrarEntregasDisponibles();
                } else {
                    document.getElementById('lista-paradas').innerHTML =
                        `<p style="text-align:center;color:#888;padding:20px;font-size:13px;">${data.error}</p>`;
                }
                return;
            }

            entregaId = data.entrega_id;
            rutaId = data.ruta_id;
            paradas = data.paradas;

            // Si ya está en camino solo se puede finalizar; si no, iniciar o regresar
            if (data.estado === 'En camino') {
                rutaIniciada = true;
                document.getElementById('btn-iniciar').style.display = 'none';
                document.getElementById('btn-regresar').style.display = 'none';
            } else {
                rutaIniciada = false;
                document.getElementById('btn-iniciar').style.display = 'block';
                document.getElementById('btn-regresar').style.display = 'block';
            }

            renderizarParadas();
            dibujarRutaEnMapa(data);
        })
        .catch(() => {
            document.getElementById('lista-paradas').innerHTML =
                '<p style="text-align:center;color:#c62828;padding:20px;font-size:13px;">Error cargando la ruta</p>';
        });
}

// ===== REGRESAR RUTA (soltar antes de iniciarla) =====
function regresarRuta() {
    if (!confirm('¿Seguro que no quieres realizar esta ruta? Quedará disponible para otro repartidor.')) return;
    if (!rutaId) return;

    fetch('/api/entregas/soltar-entrega/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruta_entrega_id: rutaId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert('Error: ' + data.error); return; }
        mostrarToast('✓ Ruta liberada');
        entregaId = null;
        rutaId = null;
        cargarRuta();
    })
    .catch(() => alert('Error de conexión'));
}


// ===== ENTREGAS DISPONIBLES (sin repartidor asignado) =====
function mostrarEntregasDisponibles() {
    document.getElementById('btn-iniciar').style.display = 'none';
    document.getElementById('info-bar').style.display = 'none';

    const lista = document.getElementById('lista-paradas');
    lista.innerHTML = '<p style="text-align:center;color:#888;padding:20px;font-size:13px;">Cargando entregas disponibles...</p>';

    fetch('/api/entregas/entregas-disponibles/')
        .then(res => res.json())
        .then(data => {
            const entregas = data.entregas || [];

            if (entregas.length === 0) {
                lista.innerHTML = '<p style="text-align:center;color:#888;padding:20px;font-size:13px;">No hay entregas disponibles por ahora</p>';
                return;
            }

            lista.innerHTML = `<p style="padding:10px 15px 0;font-size:13px;color:#888;">Entregas disponibles</p>`;

            entregas.forEach(e => {
                const div = document.createElement('div');
                div.className = 'parada-item';
                div.style.cursor = 'pointer';
                div.innerHTML = `
                    <div class="parada-num almacen">📦</div>
                    <div class="parada-info">
                        <div class="parada-nombre">Entrega #${e.entrega_id}</div>
                        <div class="parada-sub">Ruta #${e.ruta_entrega_id} · ${e.total_pedidos} pedidos · ${e.peso_total_kg.toFixed(1)} kg</div>
                        <div class="parada-sub">🚚 ${e.placas || 'sin vehículo'} · ${e.modelo || ''}</div>
                    </div>
                    <button class="btn-iniciar-ruta" style="padding:6px 14px;font-size:12px;white-space:nowrap;"
                        onclick="event.stopPropagation(); tomarYIniciarEntrega(${e.ruta_entrega_id}, ${e.entrega_id})">
                        ▶ Iniciar
                    </button>
                `;
                // Clic en la fila = solo tomarla y ver el detalle (con botón Iniciar arriba)
                div.onclick = () => tomarEntrega(e.ruta_entrega_id);
                lista.appendChild(div);
            });
        })
        .catch(() => {
            lista.innerHTML = '<p style="text-align:center;color:#c62828;padding:20px;font-size:13px;">No se pudieron cargar las entregas disponibles</p>';
        });
}

// Toma la entrega y arranca la ruta de una sola vez (botón "▶ Iniciar" de la lista)
function tomarYIniciarEntrega(rutaEntregaId, entregaIdParam) {
    fetch('/api/entregas/tomar-entrega/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruta_entrega_id: rutaEntregaId })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) {
            alert(data.error || 'No se pudo tomar la entrega');
            mostrarEntregasDisponibles();
            return Promise.reject('ya-tomada');
        }
        return fetch('/api/entregas/iniciar-ruta/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ entrega_id: entregaIdParam })
        }).then(res => res.json());
    })
    .then(data => {
        if (!data) return;
        if (data.error) { alert('Error: ' + data.error); return; }
        mostrarToast('✓ Ruta tomada e iniciada');
        cargarRuta();
    })
    .catch(err => { if (err !== 'ya-tomada') console.error(err); });
}

function tomarEntrega(rutaEntregaId) {
    fetch('/api/entregas/tomar-entrega/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruta_entrega_id: rutaEntregaId })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) {
            alert(data.error || 'No se pudo tomar la entrega');
            mostrarEntregasDisponibles(); // refresca, por si alguien más ya se la ganó
            return;
        }
        mostrarToast('✓ Entrega tomada');
        cargarRuta();
    })
    .catch(() => alert('Error de conexión'));
}


// ===== RENDERIZAR LISTA DE PARADAS =====
function renderizarParadas() {
    const lista = document.getElementById('lista-paradas');
    lista.innerHTML = '';

    const pendientes = paradas.filter(p => p.tipo === 'establecimiento' && !p.entregado).length;
    document.getElementById('info-pendientes').innerText = `${pendientes} pendientes`;

    paradas.forEach((p, i) => {
        if (p.tipo === 'almacen') {
            const div = document.createElement('div');
            div.className = 'parada-item';
            div.style.cursor = 'default';
            div.innerHTML = `
                <div class="parada-num almacen">🏭</div>
                <div class="parada-info">
                    <div class="parada-nombre">${p.nombre}</div>
                    <div class="parada-sub">Punto de salida</div>
                </div>
            `;
            lista.appendChild(div);
            return;
        }

        const div = document.createElement('div');
        div.className = `parada-item ${p.entregado ? 'entregada' : ''}`;
        div.id = `parada-${p.establecimiento_id}`;
        div.innerHTML = `
            <div class="parada-num ${p.entregado ? 'entregada' : ''}">${p.entregado ? '✓' : i}</div>
            <div class="parada-info">
                <div class="parada-nombre">${p.nombre}</div>
                <div class="parada-sub">${p.colonia} · Pedido #${p.pedido_id}</div>
            </div>
            <div class="parada-monto">$${parseFloat(p.subtotal || 0).toFixed(2)}</div>
        `;

        if (!p.entregado) {
            div.onclick = () => abrirModalParada(p);
        }

        lista.appendChild(div);
    });
}

// ===== DIBUJAR RUTA EN MAPA =====
function dibujarRutaEnMapa(data) {
    if (!data.geometria) return;

    if (rutaLayer) mapa.removeLayer(rutaLayer);
    Object.values(marcadores).forEach(m => mapa.removeLayer(m));
    marcadores = {};

    const coords = data.geometria.coordinates.map(c => [c[1], c[0]]);
    rutaLayer = L.polyline(coords, { color: '#1565c0', weight: 5, opacity: 0.8 }).addTo(mapa);

    data.paradas.forEach((p, i) => {
        const color = p.tipo === 'almacen' ? '#7b1fa2' : (p.entregado ? '#2e7d32' : '#1565c0');
        const icono = L.divIcon({
            className: '',
            html: `<div style="background:${color};color:white;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3);">${p.tipo === 'almacen' ? '🏭' : (p.entregado ? '✓' : i)}</div>`,
            iconAnchor: [14, 14]
        });

        const m = L.marker([p.lat, p.lon], { icon: icono })
            .addTo(mapa)
            .bindPopup(`<b>${p.nombre}</b>${p.tipo !== 'almacen' ? `<br>Pedido #${p.pedido_id}` : ''}`);

        if (p.tipo !== 'almacen' && !p.entregado) {
            m.on('click', () => abrirModalParada(p));
        }

        marcadores[p.establecimiento_id || 'almacen'] = m;
    });

    mapa.fitBounds(rutaLayer.getBounds(), { padding: [30, 30] });

    // Mostrar info bar
    document.getElementById('info-bar').style.display = 'flex';
    document.getElementById('info-distancia').innerText = `${data.distancia_total_km} km`;
    document.getElementById('info-duracion').innerText = `${data.duracion_total_min} min`;
}

// ===== INICIAR RUTA =====
function iniciarRuta() {
    if (!entregaId) return;

    fetch('/api/entregas/iniciar-ruta/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entrega_id: entregaId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert('Error: ' + data.error); return; }
        rutaIniciada = true;
        document.getElementById('btn-iniciar').style.display = 'none';
        mostrarToast('✓ Ruta iniciada');
    });
}

// ===== FINALIZAR RUTA =====

// ===== MODAL PARADA =====
function abrirModalParada(parada) {
    if (!rutaIniciada) {
        alert('Debes iniciar la ruta primero');
        return;
    }

    paradaActual = parada;

    habilitarConfirmacion(false);
    document.getElementById('btn-abrir-cobro').style.display = 'block';
    document.getElementById('cobro-monto').value = parseFloat(parada.subtotal || 0).toFixed(2);

   // El cobro pudo registrarse en una sesión anterior: se consulta el
    // estado real para no obligar a cobrar dos veces
    actualizarEstadoCobroModal(parada.pedido_id);

    document.getElementById('modal-est-nombre').innerText = parada.nombre;
    document.getElementById('modal-est-direccion').innerText =
        `${parada.calle} ${parada.num_ext}, ${parada.colonia}`;
    document.getElementById('cobro-est-nombre').innerText = parada.nombre;
    document.getElementById('dev-est-nombre').innerText = parada.nombre;

    // Info del pedido
    // RF36: la confirmación de entrega debe indicar fecha y hora.
    // Se muestran aquí para que el repartidor vea el momento que se
    // registrará al confirmar la entrega de este pedido.
    const { fechaTexto, horaTexto } = obtenerFechaHoraActual();
    document.getElementById('modal-pedido-info').innerHTML = `
        <div class="pedido-row">
            <span class="label">Pedido</span>
            <span class="valor">#${parada.pedido_id}</span>
        </div>
        <div class="pedido-row">
            <span class="label">Total a cobrar</span>
            <span class="monto" id="modal-total-cobrar">$${parseFloat(parada.subtotal || 0).toFixed(2)}</span>
        </div>
        <div class="pedido-row">
            <span class="label">Representante</span>
            <span class="valor">${parada.representante || '-'}</span>
        </div>
        <div class="pedido-row">
            <span class="label">Teléfono</span>
            <span class="valor">${parada.telefono || '-'}</span>
        </div>
        <div class="pedido-row">
            <span class="label">Fecha de entrega</span>
            <span class="valor" id="modal-fecha-entrega">${fechaTexto}</span>
        </div>
        <div class="pedido-row">
            <span class="label">Hora de entrega</span>
            <span class="valor" id="modal-hora-entrega">${horaTexto}</span>
        </div>
    `;

    // Cargar detalle del pedido
    // Cargar detalle del pedido
    document.getElementById('modal-productos').innerHTML = '';
    document.getElementById('modal-productos-cancelados').innerHTML = '';
    fetch(`/api/entregas/pedido/${parada.pedido_id}/detalle/`)
        .then(res => res.json())
        .then(data => {
            if (data.productos && data.productos.length > 0) {
                let html = '<div class="modal-divider"></div>';
                data.productos.forEach(p => {
                    html += `
                        <div class="producto-item">
                            <div>
                                <div class="producto-nombre">${p.nombre}</div>
                                <div class="producto-cantidad">${p.cantidad} piezas</div>
                            </div>
                            <div class="producto-importe">$${parseFloat(p.importe).toFixed(2)}</div>
                        </div>
                    `;
                });
                document.getElementById('modal-productos').innerHTML = html;
            }

            if (data.cancelados && data.cancelados.length > 0) {
                let htmlCancel = '<div class="modal-divider"></div><div class="cancelados-titulo">⚠️ Productos no disponibles</div>';
                data.cancelados.forEach(c => {
                    const fechaTexto = c.fecha_disponible_estimada
                        ? new Date(c.fecha_disponible_estimada + 'T00:00:00').toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' })
                        : 'Sin fecha estimada';
                    htmlCancel += `
                        <div class="producto-cancelado-item">
                            <div class="producto-nombre">${c.nombre}</div>
                            <div class="producto-cancelado-detalle">
                                Solicitado: ${c.cantidad_solicitada} piezas · ${c.motivo || 'Sin stock disponible'}
                            </div>
                            <div class="producto-cancelado-fecha">📅 Disponible aprox.: ${fechaTexto}</div>
                        </div>
                    `;
                });
                document.getElementById('modal-productos-cancelados').innerHTML = htmlCancel;
            }
        });

    // Mover mapa al establecimiento
    if (mapa && parada.lat && parada.lon) {
        mapa.setView([parada.lat, parada.lon], 15);
        marcadores[parada.establecimiento_id]?.openPopup();
    }

    document.getElementById('modal-parada').classList.add('visible');
}


function actualizarEstadoCobroModal(pedidoId) {
    fetch(`/api/entregas/pedido/${pedidoId}/estado-cobro/`)
        .then(r => r.json())
        .then(d => {
            const btnCobro = document.getElementById('btn-abrir-cobro');
            const aviso = document.getElementById('aviso-cobro');

            const totalSpan = document.getElementById('modal-total-cobrar');
            if (totalSpan && d.total_neto !== undefined) {
                totalSpan.innerText = `$${d.total_neto.toFixed(2)}`;
            }

            if (d.pagado) {
                habilitarConfirmacion(true);
                btnCobro.style.display = 'none';
                aviso.innerText = d.devuelto > 0
                    ? '✓ Sin saldo pendiente (con devolución aplicada)'
                    : '✓ Cobro ya registrado';
                aviso.style.display = 'block';
                aviso.style.color = '#2e7d32';
            } else {
                btnCobro.style.display = 'block';
                document.getElementById('cobro-monto').value = d.pendiente.toFixed(2);
                habilitarConfirmacion(false);
            }
        })
        .catch(() => {});
}


function cerrarModalParada(e) {
    if (!e || e.target === document.getElementById('modal-parada')) {
        document.getElementById('modal-parada').classList.remove('visible');
    }
}

// ===== MODAL COBRO =====
function abrirCobro() {
    document.getElementById('modal-parada').classList.remove('visible');
    document.getElementById('cobro-monto').value = parseFloat(paradaActual.subtotal || 0).toFixed(2);
    tipoPagoSeleccionado = 'TP001';
    document.querySelectorAll('.tipo-pago-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-efectivo').classList.add('active');
    document.getElementById('datos-tarjeta').style.display = 'none';
    document.getElementById('tarjeta-numero').value = '';
    document.getElementById('tarjeta-vencimiento').value = '';
    document.getElementById('tarjeta-cvv').value = '';
    limpiarErroresTarjeta();
    document.getElementById('modal-cobro').classList.add('visible');
}

function cerrarModalCobro(e) {
    if (!e || e.target === document.getElementById('modal-cobro')) {
        document.getElementById('modal-cobro').classList.remove('visible');
        document.getElementById('modal-parada').classList.add('visible');
    }
}

function seleccionarPago(tipo, btn) {
    tipoPagoSeleccionado = tipo;
    document.querySelectorAll('.tipo-pago-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const datosTarjeta = document.getElementById('datos-tarjeta');
    datosTarjeta.style.display = tipo === 'TP002' ? 'block' : 'none';
    if (tipo !== 'TP002') limpiarErroresTarjeta();
}

// ===== VALIDACION DE TARJETA (simulada, no se envia al backend) =====
document.addEventListener('DOMContentLoaded', () => {
    const inputNumero = document.getElementById('tarjeta-numero');
    const inputVencimiento = document.getElementById('tarjeta-vencimiento');
    const inputCvv = document.getElementById('tarjeta-cvv');

    if (inputNumero) {
        inputNumero.addEventListener('input', () => {
            let soloNumeros = inputNumero.value.replace(/\D/g, '').slice(0, 16);
            inputNumero.value = soloNumeros.replace(/(.{4})/g, '$1 ').trim();
        });
    }

    if (inputVencimiento) {
        inputVencimiento.addEventListener('input', () => {
            let soloNumeros = inputVencimiento.value.replace(/\D/g, '').slice(0, 4);
            if (soloNumeros.length >= 3) {
                inputVencimiento.value = soloNumeros.slice(0, 2) + '/' + soloNumeros.slice(2);
            } else {
                inputVencimiento.value = soloNumeros;
            }
        });
    }

    if (inputCvv) {
        inputCvv.addEventListener('input', () => {
            inputCvv.value = inputCvv.value.replace(/\D/g, '').slice(0, 4);
        });
    }
});

function limpiarErroresTarjeta() {
    ['tarjeta-numero', 'tarjeta-vencimiento', 'tarjeta-cvv'].forEach(id => {
        document.getElementById(id)?.classList.remove('input-invalido');
        const err = document.getElementById(`error-${id}`);
        if (err) err.innerText = '';
    });
}

function validarDatosTarjeta() {
    limpiarErroresTarjeta();
    let valido = true;

    const numero = document.getElementById('tarjeta-numero').value.replace(/\s/g, '');
    if (!/^\d{16}$/.test(numero)) {
        marcarError('tarjeta-numero', 'El número debe tener 16 dígitos');
        valido = false;
    }

    const vencimiento = document.getElementById('tarjeta-vencimiento').value;
    const match = vencimiento.match(/^(\d{2})\/(\d{2})$/);
    if (!match) {
        marcarError('tarjeta-vencimiento', 'Formato MM/AA');
        valido = false;
    } else {
        const mes = parseInt(match[1], 10);
        const anio = parseInt('20' + match[2], 10);

        if (mes < 1 || mes > 12) {
            marcarError('tarjeta-vencimiento', 'Mes inválido');
            valido = false;
        } else {
            const ahora = new Date();
            const finDeMes = new Date(anio, mes, 0);
            if (finDeMes < new Date(ahora.getFullYear(), ahora.getMonth(), 1)) {
                marcarError('tarjeta-vencimiento', 'Tarjeta vencida');
                valido = false;
            }
        }
    }

    const cvv = document.getElementById('tarjeta-cvv').value;
    if (!/^\d{3,4}$/.test(cvv)) {
        marcarError('tarjeta-cvv', '3 o 4 dígitos');
        valido = false;
    }

    return valido;
}

function marcarError(inputId, mensaje) {
    document.getElementById(inputId).classList.add('input-invalido');
    const err = document.getElementById(`error-${inputId}`);
    if (err) err.innerText = mensaje;
}


function guardarCobro() {
    const monto = parseFloat(document.getElementById('cobro-monto').value);
    if (!monto || monto <= 0) { alert('Ingresa un monto válido'); return; }

    if (tipoPagoSeleccionado === 'TP002' && !validarDatosTarjeta()) {
        return;
    }

    fetch('/api/entregas/registrar-cobro/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            pedido_id: paradaActual.pedido_id,
            establecimiento_id: paradaActual.establecimiento_id,
            tipo_pago: tipoPagoSeleccionado,
            monto: monto
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert('Error: ' + data.error); return; }
        document.getElementById('modal-cobro').classList.remove('visible');

        // Si el cliente pagó de más, se avisa el cambio a entregar
        if (data.cambio > 0) {
            alert(`Cobro registrado: $${data.cobrado.toFixed(2)}\n\nCambio a entregar: $${data.cambio.toFixed(2)}`);
        } else {
            mostrarToast('✓ Cobro registrado');
        }

        // Regresa al detalle de la parada y desbloquea la confirmación
        document.getElementById('modal-parada').classList.add('visible');
        habilitarConfirmacion(true);
    });
}


function habilitarConfirmacion(habilitado) {
    const btn = document.getElementById('btn-confirmar-entrega');
    const aviso = document.getElementById('aviso-cobro');
    if (!btn) return;
    btn.disabled = !habilitado;
    if (aviso) aviso.style.display = habilitado ? 'none' : 'block';
}

// ===== MODAL DEVOLUCION =====
function abrirDevolucion() {
    document.getElementById('modal-parada').classList.remove('visible');
    document.getElementById('dev-cantidad').value = '';
    document.getElementById('dev-motivo').value = '';
    document.getElementById('dev-cantidad-maxima').innerText = '';

    seleccionarTipoDevolucion('sustitucion', document.getElementById('btn-dev-sustitucion'));
    cargarProductosDevolucion();

    document.getElementById('modal-devolucion').classList.add('visible');
}

function cargarProductosDevolucion() {
    const select = document.getElementById('dev-producto');
    select.innerHTML = '<option value="">Cargando...</option>';

    fetch(`/api/entregas/pedido/${paradaActual.pedido_id}/detalle/`)
        .then(res => res.json())
        .then(data => {
            const productos = data.productos || [];
            select.innerHTML = '<option value="">Selecciona un producto...</option>' +
                productos.map(p =>
                    `<option value="${p.cod_producto}" data-cantidad="${p.cantidad}">${p.nombre} (${p.cantidad} pzas)</option>`
                ).join('');
        })
        .catch(() => {
            select.innerHTML = '<option value="">No se pudieron cargar los productos</option>';
        });
}

function actualizarMaximoDevolucion() {
    const select = document.getElementById('dev-producto');
    const opcion = select.options[select.selectedIndex];
    const maximo = opcion ? opcion.dataset.cantidad : null;

    const inputCantidad = document.getElementById('dev-cantidad');
    const etiquetaMax = document.getElementById('dev-cantidad-maxima');

    if (maximo) {
        inputCantidad.max = maximo;
        etiquetaMax.innerText = `(máx. ${maximo})`;
    } else {
        inputCantidad.removeAttribute('max');
        etiquetaMax.innerText = '';
    }
}

function cerrarModalDevolucion(e) {
    if (!e || e.target === document.getElementById('modal-devolucion')) {
        document.getElementById('modal-devolucion').classList.remove('visible');
        document.getElementById('modal-parada').classList.add('visible');
    }
}

function guardarDevolucion() {
    const selectProducto = document.getElementById('dev-producto');
    const codProducto = selectProducto.value;
    const opcionSeleccionada = selectProducto.options[selectProducto.selectedIndex];
    const maximo = opcionSeleccionada ? parseInt(opcionSeleccionada.dataset.cantidad) : null;

    const cantidad = parseInt(document.getElementById('dev-cantidad').value);
    const motivo = document.getElementById('dev-motivo').value.trim();
    const tipo = TIPOS_DEVOLUCION[tipoDevolucionActual].valor;

    if (!codProducto) { alert('Selecciona el producto a devolver'); return; }
    if (!cantidad || cantidad <= 0) { alert('Ingresa una cantidad válida'); return; }
    if (maximo && cantidad > maximo) { alert(`No puedes devolver más de ${maximo} piezas`); return; }
    if (!motivo) { alert('Ingresa el motivo de la devolución'); return; }

    // Doble confirmación para la acción irreversible
    if (tipoDevolucionActual === 'completa') {
        if (!confirm('Esta acción cancela definitivamente el producto de la venta. ¿Continuar?')) return;
    }

    fetch('/api/entregas/registrar-devolucion/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            entrega_id: entregaId,
            pedido_id: paradaActual.pedido_id,
            cod_producto: codProducto,
            cantidad: cantidad,
            motivo: tipo,
            descripcion: motivo
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert('Error: ' + data.error); return; }
        document.getElementById('modal-devolucion').classList.remove('visible');
        mostrarToast('✓ Devolución registrada');

        document.getElementById('modal-parada').classList.add('visible');
        actualizarEstadoCobroModal(paradaActual.pedido_id);
    });
}

// ===== FECHA Y HORA (RF36) =====
// Devuelve la fecha/hora actual en formato legible (para mostrar en el
// modal) y en formato ISO (para enviar al backend).
function obtenerFechaHoraActual() {
    const ahora = new Date();

    const pad = n => String(n).padStart(2, '0');
    const fechaISO = `${ahora.getFullYear()}-${pad(ahora.getMonth() + 1)}-${pad(ahora.getDate())}`;
    const horaISO = `${pad(ahora.getHours())}:${pad(ahora.getMinutes())}:${pad(ahora.getSeconds())}`;

    const fechaTexto = ahora.toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const horaTexto = ahora.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });

    return { fechaISO, horaISO, fechaTexto, horaTexto };
}

// ===== CONFIRMAR ENTREGA =====
function confirmarEntrega() {
    // RF36: se registra la fecha y hora exactas en las que el repartidor
    // confirma la entrega.
    const { fechaISO, horaISO, fechaTexto, horaTexto } = obtenerFechaHoraActual();

    fetch('/api/entregas/confirmar-entrega/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            pedido_id: paradaActual.pedido_id,
            establecimiento_id: paradaActual.establecimiento_id,
            entrega_id: entregaId,
            fecha_entrega: fechaISO,
            hora_entrega: horaISO
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert('Error: ' + data.error); return; }

        // Marcar parada como entregada
        const idx = paradas.findIndex(p => p.establecimiento_id === paradaActual.establecimiento_id);
        if (idx !== -1) paradas[idx].entregado = true;

        cerrarModalParada();
        renderizarParadas();

        // Actualizar marcador en mapa
        const m = marcadores[paradaActual.establecimiento_id];
        if (m) {
            const icono = L.divIcon({
                className: '',
                html: `<div style="background:#2e7d32;color:white;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3);">✓</div>`,
                iconAnchor: [14, 14]
            });
            m.setIcon(icono);
        }

        mostrarToast(`✓ Entrega confirmada · ${fechaTexto} ${horaTexto}`);

        // RF37: el sistema cerró la entrega al quedar todos los pedidos entregados
        if (data.entrega_completada) {
            setTimeout(() => {
                alert('✓ Ruta completada\n\nTodos los pedidos fueron entregados. La entrega se cerró automáticamente.');
                location.reload();
            }, 800);
        }
    });
}

// ===== TOAST =====
function mostrarToast(msg) {
    const toast = document.getElementById('toast');
    toast.innerText = msg;
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 3000);
}

// ===== INICIALIZAR =====
window.addEventListener('load', () => {
    inicializarMapa();
    cargarRuta();
});

// ===== MODAL DEVOLUCION =====
// ===== MODAL DEVOLUCION =====
const TIPOS_DEVOLUCION = {
    sustitucion: {
        valor: 'Producto dañado con sustitución',
        etiqueta: '✓ Registrar devolución con sustitución',
        clase: 'btn-confirmar-dev--sustitucion'
    },
    completa: {
        valor: 'Devolución completa sin reemplazo',
        etiqueta: '⚠ Confirmar devolución completa sin reemplazo',
        clase: 'btn-confirmar-dev--completa'
    }
};

let tipoDevolucionActual = 'sustitucion';

function seleccionarTipoDevolucion(tipo, btn) {
    tipoDevolucionActual = tipo;

    document.querySelectorAll('.tipo-dev-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const confirmar = document.getElementById('btn-guardar-dev');
    confirmar.classList.remove('btn-confirmar-dev--sustitucion', 'btn-confirmar-dev--completa');
    confirmar.classList.add(TIPOS_DEVOLUCION[tipo].clase);
    confirmar.innerText = TIPOS_DEVOLUCION[tipo].etiqueta;
}

