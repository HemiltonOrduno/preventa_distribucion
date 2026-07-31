/*
  RF09-10: al llegar a esta pantalla, el sistema marca automáticamente
  la visita como "En proceso" (llegar aquí ES la acción de "Realizar
  visita"). RF11/RF14 se disparan con los botones de abajo.
*/
const params = new URLSearchParams(window.location.search);
const visitaId = params.get('visita_id');
const nombreEstablecimiento = params.get('nombre');

document.getElementById("nombreEstablecimiento").textContent = nombreEstablecimiento || 'Establecimiento';

async function marcarEnProceso(){
    if (!visitaId) return;
    await fetch(`/api/visitas/api/visitas/${visitaId}/realizar/`, { method: 'PATCH' });
}

function irALevantarPedido(){
    window.location.href = `/api/visitas/levantar-pedido/?visita_id=${visitaId}`;
}

function irAVisitaSinPedido(){
    window.location.href = `/api/visitas/visita-sin-pedido/?visita_id=${visitaId}`;
}

marcarEnProceso();