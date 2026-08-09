import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from usuarios.permissions import rol_requerido, rol_requerido

@csrf_exempt
@rol_requerido('Vendedor', 'Administrador')
def registro_cliente_view(request):
    return render(request, 'establecimientos/registro_cliente.html')


@csrf_exempt
@rol_requerido('Vendedor', 'Administrador')
def registro_establecimiento_view(request):
    return render(request, 'establecimientos/registro_establecimiento.html')


@csrf_exempt
def crear_cliente(request):
    """
    RF01: registrar un nuevo cliente (rep_establecimiento) durante la
    visita en campo.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    empleado_num = request.session.get('empleado_num')
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    campos_requeridos = ['nombre_de_pila', 'apellido_paterno', 'rfc', 'telefono', 'email']
    faltantes = [c for c in campos_requeridos if not body.get(c)]
    if faltantes:
        return JsonResponse({"error": f"Faltan campos: {', '.join(faltantes)}"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO rep_establecimiento
                    (rfc, repNombre, repApellPat, repApellMa, telefono,
                     email, fecha_registro, empleado, edo_rep_establecimiento)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, 'ERE001')
            """, [
                body['rfc'],
                body['nombre_de_pila'],
                body['apellido_paterno'],
                body.get('apellido_materno') or None,
                body['telefono'],
                body['email'],
                empleado_num,
            ])
            nuevo_numero = cursor.lastrowid

    return JsonResponse({
        "mensaje": "Cliente registrado correctamente",
        "rep_establecimiento_id": nuevo_numero
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def crear_establecimiento(request):
    """
    RF02: registrar el establecimiento asociado al cliente recién creado.
    RF03: el sistema asigna zona y estado "Activo" automáticamente,
    según la ubicación (lat/lon) del establecimiento.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    empleado_num = request.session.get('empleado_num')
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    campos_requeridos = ['nombre', 'calle', 'numero', 'colonia', 'rep_establecimiento_id', 'latitud', 'longitud']
    faltantes = [c for c in campos_requeridos if body.get(c) in (None, '')]
    if faltantes:
        return JsonResponse({"error": f"Faltan campos: {', '.join(faltantes)}"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            # RF03: la zona se asigna automáticamente según en qué rango
            # de lat/lon cae el establecimiento
            cursor.execute("""
                SELECT num FROM zona
                WHERE %s BETWEEN lat_min AND lat_max
                  AND %s BETWEEN lon_min AND lon_max
                LIMIT 1
            """, [body['latitud'], body['longitud']])
            zona_row = cursor.fetchone()
            if not zona_row:
                return JsonResponse({"error": "No se encontró una zona para esta ubicación"}, status=400)
            zona_id = zona_row[0]

            cursor.execute("""
                INSERT INTO establecimiento
                    (nombre, estCalle, estNumero, estColonia, telefono,
                     latitud, longitud, fecha_registro, zona, empleado,
                     entrega, rep_establecimiento, edo_establecimiento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, NULL, %s, 'EST001')
            """, [
                body['nombre'],
                body['calle'],
                body['numero'],
                body['colonia'],
                body.get('telefono') or '',
                body['latitud'],
                body['longitud'],
                zona_id,
                empleado_num,
                body['rep_establecimiento_id'],
            ])
            nuevo_numero = cursor.lastrowid

    return JsonResponse({
        "mensaje": "Establecimiento registrado correctamente",
        "establecimiento_id": nuevo_numero,
        "zona_id": zona_id
    }, json_dumps_params={'ensure_ascii': False})


@rol_requerido('Vendedor', 'Administrador')
def clientes_registrados(request):
    """
    Lista los clientes activos para poder asociarles un establecimiento
    adicional sin registrarlos de nuevo (RF02).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.numero AS id,
                   CONCAT(r.repNombre, ' ', r.repApellPat,
                          COALESCE(CONCAT(' ', r.repApellMa), '')) AS nombre,
                   r.rfc, r.telefono,
                   COUNT(e.numero) AS establecimientos
            FROM rep_establecimiento r
            LEFT JOIN establecimiento e ON e.rep_establecimiento = r.numero
            WHERE r.edo_rep_establecimiento = 'ERE001'
            GROUP BY r.numero, r.repNombre, r.repApellPat, r.repApellMa, r.rfc, r.telefono
            ORDER BY r.repApellPat, r.repNombre
        """)
        columns = [c[0] for c in cursor.description]
        clientes = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({"clientes": clientes}, json_dumps_params={'ensure_ascii': False})



# --- Placeholders restantes, pendientes ---
class EstablecimientoListCreate:
    pass


class EstablecimientoDetail:
    pass


class RepEstablecimientoListCreate:
    pass


class RepEstablecimientoDetail:
    pass