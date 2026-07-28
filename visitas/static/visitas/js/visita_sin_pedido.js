/*
  Falta: el fetch que envíe el motivo real (RF14-15) antes de
  redirigir. Por ahora solo navega de vuelta a la ruta del día,
  simulando "siguiente destino" (RF12).
*/
function completarVisitaSinPedido(){
    const motivo = document.getElementById("motivo").value.trim();
    if (motivo === ""){
        alert("Escribe el motivo antes de completar la visita.");
        return;
    }
    console.log("Pendiente: enviar visita sin pedido con motivo:", motivo);
    window.location.href = '/api/visitas/ruta-del-dia/';
}