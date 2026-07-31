/*
  RF01: envía el cliente nuevo y continúa al registro del
  establecimiento con el id del cliente ya creado.
*/
async function continuarARegistroEstablecimiento(event){
    event.preventDefault();

    const datos = {
        nombre_de_pila: document.getElementById("nombre_de_pila").value,
        apellido_paterno: document.getElementById("apellido_paterno").value,
        apellido_materno: document.getElementById("apellido_materno").value,
        rfc: document.getElementById("rfc").value,
        telefono: document.getElementById("telefono").value,
        email: document.getElementById("email").value
    };

    const res = await fetch('/api/establecimientos/clientes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    });
    const data = await res.json();

    if (!res.ok){
        alert(data.error || 'No se pudo registrar el cliente');
        return false;
    }

    window.location.href = `/api/establecimientos/registro-establecimiento/?rep_establecimiento_id=${data.rep_establecimiento_id}`;
    return false;
}