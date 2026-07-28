/*
  Falta: el fetch que envíe los datos reales del cliente (RF01)
  antes de redirigir al registro del establecimiento.
*/
function continuarARegistroEstablecimiento(event){
    event.preventDefault();

    const datos = {
        nombre_de_pila: document.getElementById("nombre_de_pila").value,
        apellido_paterno: document.getElementById("apellido_paterno").value,
        apellido_materno: document.getElementById("apellido_materno").value,
        rfc: document.getElementById("rfc").value,
        telefono: document.getElementById("telefono").value,
        email: document.getElementById("email").value
    };

    console.log("Pendiente: enviar datos del cliente:", datos);
    window.location.href = '/api/establecimientos/registro-establecimiento/';
    return false;
}