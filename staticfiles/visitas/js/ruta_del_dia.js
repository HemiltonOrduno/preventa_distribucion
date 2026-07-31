/*
  RF07: trae el siguiente destino de la ruta del vendedor y lo pinta
  en pantalla. RF08 se dispara al dar clic en "Iniciar visita".
*/
let destinoActual = null;

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

        contenedor.innerHTML = `
            <div class="card">
                <div class="card__row">
                    <i class='bx bx-store'></i>
                    <span class="card__title">${data.nombre}</span>
                </div>
                <p class="card__sub">${data.estCalle} ${data.estNumero}, ${data.estColonia}</p>
                <span class="badge badge--info">${data.zona_nombre}</span>
            </div>
            <button class="btn btn--primary" onclick="iniciarVisita()">
                Iniciar visita
                <i class='bx bx-right-arrow-alt'></i>
            </button>`;

    } catch (err) {
        contenedor.innerHTML = `<p style="font-size:13px;color:var(--color-danger-text)">No se pudo cargar la ruta</p>`;
    }
}

async function iniciarVisita(){
    if (!destinoActual) return;

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
        alert(data.error || 'No se pudo iniciar la visita');
        return;
    }

    window.location.href = `/api/visitas/visita/?visita_id=${data.visita_id}&nombre=${encodeURIComponent(destinoActual.nombre)}`;
}

cargarRutaDelDia();