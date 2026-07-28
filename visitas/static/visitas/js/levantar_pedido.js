/*
  Falta: el fetch que envíe el pedido real (RF04-06) antes de
  redirigir. Por ahora solo navega de vuelta a la ruta del día,
  simulando "siguiente destino" (RF12).
*/
function cambiarCantidad(boton, delta){
    const contenedor = boton.closest(".qty");
    const valorSpan = contenedor.querySelector(".qty__value");
    let valor = parseInt(valorSpan.textContent, 10) + delta;
    if (valor < 0) valor = 0;
    valorSpan.textContent = valor;
}

function confirmarPedido(){
    const observaciones = document.getElementById("observaciones").value;
    console.log("Pendiente: enviar pedido con observaciones:", observaciones);
    window.location.href = '/api/visitas/ruta-del-dia/';
}