/*
  RF07: trae el siguiente destino de la ruta del vendedor y lo pinta
  en pantalla.

  Flujo de la jornada:
    "Iniciar ruta"  -> una sola vez al empezar el dia. Pasa la ruta de
                       Asignada a Iniciada y deja la primera visita
                       En camino (EVI002).                        RF08
    "Realizar visita" -> en cada establecimiento, al llegar. Pasa la
                       visita a En proceso (EVI003).           RF09-RF10
    Levantar pedido / Establecimiento cerrado                RF11, RF14

  Al completar una parada el vendedor ya va rumbo a la siguiente, asi
  que la visita del proximo establecimiento se abre En camino sola, sin
  pedir otro clic. El estado En camino se conserva hasta que presione
  "Realizar visita", que es lo que exige el RF08.

  La pantalla se dibuja segun el estado que reporta la API, asi que
  si el vendedor cierra el navegador a medio camino, al volver retoma
  el paso donde se quedo en vez de empezar de cero.

  Ademas, dibuja el mapa de toda la ruta del dia (visitadas, actual,
  pendientes) para que el vendedor se ubique.
*/
let destinoActual = null;
let visitaEnProcesoId = null;
let mapaVendedor = null;
let marcadoresMapa = [];
let rutaLayerVendedor = null;

const ALMACEN_ICONO = () => L.divIcon({
    className: '',
    html: `<div style="background:#7b1fa2;color:white;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3);">🏭</div>`,
    iconAnchor: [13, 13]
});

function iconoParada(color, numero) {
    return L.divIcon({
        className: '',
        html: `<div style="background:${color};color:white;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3);">${numero}</div>`,
        iconAnchor: [12, 12]
    });
}

function colorPorEstado(estado) {
    if (estado === 'completada') return '#2e7d32';
    if (estado === 'actual') return '#c62828';
    return '#9e9e9e';
}

function inicializarMapaVendedor() {
    if (mapaVendedor) return;
    mapaVendedor = L.map('mapaVendedor', { zoomControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(mapaVendedor);
}

async function cargarMapaRuta() {
    inicializarMapaVendedor();

    try {
        const res = await fetch('/api/visitas/api/mapa-ruta-del-dia/');
        const data = await res.json();
        if (!res.ok) return;

        marcadoresMapa.forEach(m => mapaVendedor.removeLayer(m));
        marcadoresMapa = [];

        const puntos = [];

        if (data.almacen) {
            const m = L.marker([data.almacen.lat, data.almacen.lon], { icon: ALMACEN_ICONO() })
                .addTo(mapaVendedor)
                .bindPopup(`<b>${data.almacen.nombre}</b><br>Punto de salida`);
            marcadoresMapa.push(m);
            puntos.push([data.almacen.lat, data.almacen.lon]);
        }

        data.paradas.forEach((p, i) => {
            const color = colorPorEstado(p.estado);
            const m = L.marker([p.latitud, p.longitud], { icon: iconoParada(color, i + 1) })
                .addTo(mapaVendedor)
                .bindPopup(`<b>${p.nombre}</b><br>${p.colonia}`);
            marcadoresMapa.push(m);
            puntos.push([p.latitud, p.longitud]);
        });

        // Traza la ruta por calles (OSRM); si no hay geometría,
        // une los puntos con una línea recta punteada como respaldo
        if (rutaLayerVendedor) {
            mapaVendedor.removeLayer(rutaLayerVendedor);
            rutaLayerVendedor = null;
        }

        if (data.geometria && data.geometria.coordinates) {
            const coords = data.geometria.coordinates.map(c => [c[1], c[0]]);
            rutaLayerVendedor = L.polyline(coords, {
                color: '#1a237e', weight: 4, opacity: 0.75
            }).addTo(mapaVendedor);
        } else if (puntos.length >= 2) {
            rutaLayerVendedor = L.polyline(puntos, {
                color: '#9e9e9e', weight: 3, opacity: 0.6, dashArray: '6,6'
            }).addTo(mapaVendedor);
        }

        setTimeout(() => {
            mapaVendedor.invalidateSize();
            if (puntos.length > 0) {
                mapaVendedor.fitBounds(puntos, { padding: [30, 30] });
            }
        }, 100);

    } catch (err) {
        console.warn('No se pudo cargar el mapa de la ruta');
    }
}

/* Inicio de jornada: la ruta esta Asignada y todavia no arranca.
   Este boton sale UNA sola vez, en la primera parada del dia. */
function renderTarjetaInicioRuta() {
    const contenedor = document.getElementById("contenidoRuta");
    contenedor.innerHTML = `
        <div class="card">
            <div class="card__row">
                <i class='bx bx-store'></i>
                <span class="card__title">${destinoActual.nombre}</span>
            </div>
            <p class="card__sub">${destinoActual.estCalle} ${destinoActual.estNumero}, ${destinoActual.estColonia}</p>
            <span class="badge badge--info">${destinoActual.zona_nombre}</span>
        </div>
        <p style="font-size:12px;color:var(--color-text-muted);margin:0 0 .7rem">
            Este es tu primer destino. Inicia la ruta para salir a campo.
        </p>
        <button class="btn btn--primary" id="btnIniciarRuta" onclick="iniciarVisita()">
            Iniciar ruta
            <i class='bx bx-right-arrow-alt'></i>
        </button>`;
}

/* RF08: la visita ya existe y esta En camino. El vendedor va en
   trayecto; al llegar presiona "Realizar visita" (RF09). */
function renderTarjetaEnCamino() {
    const contenedor = document.getElementById("contenidoRuta");
    contenedor.innerHTML = `
        <div class="card">
            <div class="card__row">
                <i class='bx bx-store'></i>
                <span class="card__title">${destinoActual.nombre}</span>
            </div>
            <p class="card__sub">${destinoActual.estCalle} ${destinoActual.estNumero}, ${destinoActual.estColonia}</p>
            <span class="badge badge--info">En camino</span>
        </div>
        <p style="font-size:12px;color:var(--color-text-muted);margin:0 0 .7rem">
            Al llegar al establecimiento, presiona Realizar visita.
        </p>
        <button class="btn btn--primary" id="btnRealizarVisita" onclick="realizarVisita()">
            Realizar visita
            <i class='bx bx-check-circle'></i>
        </button>`;
}

function renderTarjetaEnProceso() {
    const contenedor = document.getElementById("contenidoRuta");
    contenedor.innerHTML = `
        <div class="card">
            <div class="card__row">
                <i class='bx bx-store'></i>
                <span class="card__title">${destinoActual.nombre}</span>
            </div>
            <p class="card__sub">${destinoActual.estCalle} ${destinoActual.estNumero}, ${destinoActual.estColonia}</p>
            <span class="badge badge--success">Visita iniciada</span>
        </div>
        <button class="btn btn--primary" onclick="irALevantarPedido()">
            Levantar pedido
            <i class='bx bx-cart-add'></i>
        </button>
        <button class="btn btn--danger" onclick="irAVisitaSinPedido()">
            Establecimiento cerrado
            <i class='bx bx-x-circle'></i>
        </button>`;
}

/* Aviso breve al regresar de completar una parada. El resultado llega
   como ?completada= en la URL y se limpia enseguida para que no
   reaparezca si el vendedor recarga la pagina. */
function mostrarAvisoVisitaCompletada(){
    const resultado = new URLSearchParams(window.location.search).get('completada');
    if (!resultado) return;

    const textos = {
        pedido:  '\u2714 Visita completada, pedido registrado',
        cerrado: '\u2714 Visita completada, establecimiento cerrado'
    };
    const aviso = document.createElement('div');
    aviso.className = 'aviso-visita';
    aviso.textContent = textos[resultado] || '\u2714 Visita completada';
    document.getElementById('contenidoRuta').before(aviso);

    history.replaceState(null, '', window.location.pathname);
    setTimeout(() => aviso.remove(), 4000);
}


async function cargarRutaDelDia(){
    const contenedor = document.getElementById("contenidoRuta");
    try {
        const res = await fetch('/api/visitas/api/ruta-del-dia/');
        const data = await res.json();

        if (!res.ok){
            contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-danger-text)">${data.error}</p>`;
            return;
        }

        if (data.mensaje){
            contenedor.innerHTML = `
                <div class="card">
                    <p style="font-size:13px;margin:0">${data.mensaje}</p>
                </div>`;
            return;
        }

        destinoActual = data;
        visitaEnProcesoId = data.visita_id;

        if (data.visita_estado === 'EVI003') {
            // Ya esta En proceso: el vendedor llego y abrio la visita.
            renderTarjetaEnProceso();
        } else if (data.visita_estado === 'EVI002') {
            // En camino hacia este establecimiento.
            renderTarjetaEnCamino();
        } else if (!data.ruta_iniciada) {
            // Todavia no arranca la jornada: unico momento en que
            // aparece el boton "Iniciar ruta".
            renderTarjetaInicioRuta();
        } else {
            // La ruta ya va en marcha y esta parada aun no tiene visita:
            // el vendedor viene de completar la anterior, asi que ya va
            // en camino. Se abre la visita En camino sin pedir otro clic
            // y se le muestra directo "Realizar visita".
            contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-text-muted)">Cargando siguiente parada...</p>`;
            await iniciarVisita();
        }

    } catch (err) {
        contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-danger-text)">No se pudo cargar la ruta</p>`;
    }
}

async function iniciarVisita(){
    if (!destinoActual) return;

    const boton = document.getElementById('btnIniciarRuta');
    if (boton) { boton.disabled = true; boton.style.opacity = '0.6'; }

    const res = await fetch('/api/visitas/api/visitas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ruta_visita_id: destinoActual.ruta_visita_id,
            establecimiento_id: destinoActual.numero
        })
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo iniciar la ruta');
        if (boton) { boton.disabled = false; boton.style.opacity = '1'; }
        return;
    }

    visitaEnProcesoId = data.visita_id;

    // RF08 termina aqui: la visita queda En camino. El paso a
    // En proceso lo dispara el vendedor con "Realizar visita".
    renderTarjetaEnCamino();
}


/* RF09-RF10: el vendedor llego al establecimiento y da inicio formal
   a la visita, que pasa a En proceso. */
async function realizarVisita(){
    if (!visitaEnProcesoId) return;

    const boton = document.getElementById('btnRealizarVisita');
    if (boton) { boton.disabled = true; boton.style.opacity = '0.6'; }

    const res = await fetch(`/api/visitas/api/visitas/${visitaEnProcesoId}/realizar/`, {
        method: 'PATCH'
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo iniciar la ruta');
        if (boton) { boton.disabled = false; boton.style.opacity = '1'; }
        return;
    }

    renderTarjetaEnProceso();
}

function irALevantarPedido(){
    if (!visitaEnProcesoId) return;
    window.location.href = `/api/visitas/levantar-pedido/?visita_id=${visitaEnProcesoId}`;
}

function irAVisitaSinPedido(){
    if (!visitaEnProcesoId) return;
    window.location.href = `/api/visitas/visita-sin-pedido/?visita_id=${visitaEnProcesoId}`;
}

cargarRutaDelDia();
cargarMapaRuta();

mostrarAvisoVisitaCompletada();