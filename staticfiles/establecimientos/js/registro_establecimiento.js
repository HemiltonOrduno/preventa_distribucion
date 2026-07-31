/*
  RF02: envía el establecimiento nuevo. RF03: la zona y el estado
  "Activo" los calcula el backend a partir de la ubicación; aquí solo
  obtenemos lat/lon con la geolocalización del navegador (RFN-25).
*/
const params = new URLSearchParams(window.location.search);
const repEstablecimientoId = params.get('rep_establecimiento_id');

let ubicacion = null;
const estadoUbicacion = document.getElementById("estadoUbicacion");

function actualizarEstadoUbicacion(mensaje, esError){
    const color = esError ? 'var(--color-danger-text)' : 'var(--color-info-text)';
    const icono = esError ? 'bx-error-circle' : 'bx-check-circle';
    estadoUbicacion.innerHTML = `
        <div class="card__row" style="margin-bottom:0;">
            <i class='bx ${icono}' style="color:${color};"></i>
            <span style="font-size:12px; color:${color};">${mensaje}</span>
        </div>`;
}

if (navigator.geolocation){
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            ubicacion = { lat: pos.coords.latitude, lon: pos.coords.longitude };
            actualizarEstadoUbicacion('Ubicación detectada, la zona se asignará automáticamente', false);
        },
        () => {
            actualizarEstadoUbicacion('No se pudo obtener tu ubicación, actívala e intenta de nuevo', true);
        }
    );
} else {
    actualizarEstadoUbicacion('Tu navegador no soporta geolocalización', true);
}

async function guardarEstablecimiento(event){
    event.preventDefault();

    if (!repEstablecimientoId){
        alert('Falta el cliente asociado, regresa al paso anterior');
        return false;
    }
    if (!ubicacion){
        alert('Aún no se detecta tu ubicación, espera un momento e intenta de nuevo');
        return false;
    }

    const datos = {
        nombre: document.getElementById("nombre").value,
        calle: document.getElementById("calle").value,
        numero: document.getElementById("numero").value,
        colonia: document.getElementById("colonia").value,
        telefono: document.getElementById("telefono").value,
        latitud: ubicacion.lat,
        longitud: ubicacion.lon,
        rep_establecimiento_id: repEstablecimientoId
    };

    const res = await fetch('/api/establecimientos/nuevo/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo registrar el establecimiento');
        return false;
    }

    window.location.href = '/api/visitas/ruta-del-dia/';
    return false;
}