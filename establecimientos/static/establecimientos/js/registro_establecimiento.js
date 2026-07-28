/*
  Falta: el fetch que envíe los datos reales del establecimiento
  (RF02). La zona y el estado "Activo" (RF03) los calcula el backend,
  no este script.
*/
function guardarEstablecimiento(event){
    event.preventDefault();

    const datos = {
        nombre: document.getElementById("nombre").value,
        calle: document.getElementById("calle").value,
        numero: document.getElementById("numero").value,
        colonia: document.getElementById("colonia").value
    };

    console.log("Pendiente: enviar datos del establecimiento:", datos);
    window.location.href = '/api/visitas/ruta-del-dia/';
    return false;
}