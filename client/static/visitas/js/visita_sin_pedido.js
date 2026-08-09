/*
  RF14-15: envía el motivo real y marca la visita como completada
  sin pedido.
*/
const params = new URLSearchParams(window.location.search);
const visitaId = params.get('visita_id');

async function completarVisitaSinPedido(){
    const motivo = document.getElementById("motivo").value.trim();
    if (motivo === ""){
        alert("Escribe el motivo antes de completar la visita.");
        return;
    }
    if (!visitaId){
        alert('No se encontró la visita, regresa a la ruta del día');
        return;
    }

    const res = await fetch(`/api/visitas/api/visitas/${visitaId}/sin-pedido/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ motivo })
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo completar la visita');
        return;
    }

    // El aviso lo muestra la pantalla de ruta del dia al volver
    window.location.href = '/api/visitas/ruta-del-dia/?completada=cerrado';
}