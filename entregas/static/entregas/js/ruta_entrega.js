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
    document.getElementById('cobro-monto').value = parseFloat(parada.subtotal || 0).toFixed(2);

    document.getElementById('modal-est-nombre').innerText = parada.nombre;
    document.getElementById('modal-est-direccion').innerText = parada.colonia;
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
            <span class="monto">$${parseFloat(parada.subtotal || 0).toFixed(2)}</span>
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
    document.getElementById('modal-productos').innerHTML = '';
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
        });

    // Mover mapa al establecimiento
    if (mapa && parada.lat && parada.lon) {
        mapa.setView([parada.lat, parada.lon], 15);
        marcadores[parada.establecimiento_id]?.openPopup();
    }

    document.getElementById('modal-parada').classList.add('visible');
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
}

function guardarCobro() {
    const monto = parseFloat(document.getElementById('cobro-monto').value);
    if (!monto || monto <= 0) { alert('Ingresa un monto válido'); return; }

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
        mostrarToast('✓ Cobro registrado');
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
    document.getElementById('modal-devolucion').classList.add('visible');
}

function cerrarModalDevolucion(e) {
    if (!e || e.target === document.getElementById('modal-devolucion')) {
        document.getElementById('modal-devolucion').classList.remove('visible');
        document.getElementById('modal-parada').classList.add('visible');
    }
}

function guardarDevolucion() {
    const cantidad = parseInt(document.getElementById('dev-cantidad').value);
    const motivo = document.getElementById('dev-motivo').value.trim();
    const tipo = TIPOS_DEVOLUCION[tipoDevolucionActual].valor;

    if (!cantidad || cantidad <= 0) { alert('Ingresa una cantidad válida'); return; }
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

    // El botón de confirmar hereda el color del tipo seleccionado
    const confirmar = document.getElementById('btn-guardar-dev');
    confirmar.classList.remove('btn-confirmar-dev--sustitucion', 'btn-confirmar-dev--completa');
    confirmar.classList.add(TIPOS_DEVOLUCION[tipo].clase);
    confirmar.innerText = TIPOS_DEVOLUCION[tipo].etiqueta;
}

function abrirDevolucion() {
    document.getElementById('modal-parada').classList.remove('visible');
    document.getElementById('dev-cantidad').value = '';
    document.getElementById('dev-motivo').value = '';

    // Siempre arranca en la opción de menor impacto
    seleccionarTipoDevolucion('sustitucion', document.getElementById('btn-dev-sustitucion'));

    document.getElementById('modal-devolucion').classList.add('visible');
}