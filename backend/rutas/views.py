from unittest import result
from django.conf import settings
import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from usuarios.permissions import rol_requerido
from datetime import date, timedelta
from django.db import connection, transaction

# Coordenadas del almacén (Pepsico El Florido, Tijuana)
ALMACEN = {
    "lon": -116.9400,
    "lat": 32.4700,
    "nombre": "Almacén Sabritas - El Florido"
}

OSRM_URL = settings.OSRM_URL

@rol_requerido('Coordinador', 'Administrador')
def coordinador(request):
    return render(request, "rutas/base_coordinador.html")

@csrf_exempt
def calcular_ruta_visita(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        body = json.loads(request.body)
        establecimientos = body.get("establecimientos", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    if not establecimientos:
        return JsonResponse({"error": "No se proporcionaron establecimientos"}, status=400)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (e["lon"], e["lat"]) for e in establecimientos
    ]
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordenadas)
    url = f"{OSRM_URL}/trip/v1/driving/{coords_str}"
    try:
        response = requests.get(url, params={
            "roundtrip": "false", "source": "first", "destination": "last",
            "geometries": "geojson", "overview": "full"
        }, timeout=10)
        data = response.json()
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar al servidor OSRM"}, status=500)
    if data.get("code") != "Ok":
        return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)

    trip = data["trips"][0]
    waypoints = data["waypoints"]
    orden = [wp["waypoint_index"] for wp in waypoints]
    paradas = []
    for i, (lon, lat) in enumerate(coordenadas):
        if i == 0:
            paradas.append({"lon": lon, "lat": lat, "nombre": ALMACEN["nombre"], "tipo": "almacen", "orden": 0})
        else:
            est = establecimientos[i - 1]
            paradas.append({"lon": lon, "lat": lat, "nombre": est.get("nombre"), "tipo": "establecimiento", "orden": orden[i], "establecimiento_id": est.get("id")})

    return JsonResponse({"distancia_total_km": round(trip["distance"] / 1000, 2), "duracion_total_min": round(trip["duration"] / 60, 2), "geometria": trip["geometry"], "paradas": paradas}, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def calcular_ruta_entrega(request):
    """
    Calcula la ruta óptima de entrega para un repartidor.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        establecimientos = body.get("establecimientos", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not establecimientos:
        return JsonResponse({"error": "No se proporcionaron establecimientos"}, status=400)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (e["lon"], e["lat"]) for e in establecimientos
    ]

    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordenadas)
    url = f"{OSRM_URL}/trip/v1/driving/{coords_str}"

    try:
        response = requests.get(url, params={
            "roundtrip": "false",
            "source": "first",
            "destination": "last",
            "geometries": "geojson",
            "overview": "full"
        }, timeout=10)
        data = response.json()
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar al servidor OSRM"}, status=500)

    if data.get("code") != "Ok":
        return JsonResponse({"error": "OSRM no pudo calcular la ruta", "detalle": data}, status=400)

    trip = data["trips"][0]
    waypoints = data["waypoints"]

    orden = [wp["waypoint_index"] for wp in waypoints]
    paradas = []
    for i, (lon, lat) in enumerate(coordenadas):
        if i == 0:
            paradas.append({
                "lon": lon,
                "lat": lat,
                "nombre": ALMACEN["nombre"],
                "tipo": "almacen",
                "orden": 0
            })
        else:
            est = establecimientos[i - 1]
            paradas.append({
                "lon": lon,
                "lat": lat,
                "nombre": est.get("nombre", f"Establecimiento {i}"),
                "tipo": "establecimiento",
                "orden": orden[i],
                "establecimiento_id": est.get("id"),
                "pedido_id": est.get("pedido_id")
            })

    return JsonResponse({
        "distancia_total_km": round(trip["distance"] / 1000, 2),
        "duracion_total_min": round(trip["duration"] / 60, 2),
        "geometria": trip["geometry"],
        "paradas": paradas
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def obtener_establecimientos_entrega(request, entrega_id):
    """
    Obtiene los establecimientos de una entrega para mostrarlos en el mapa.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.numero AS establecimiento_id,
                e.nombre AS establecimiento_nombre,
                e.latitud,
                e.longitud,
                e.estColonia AS colonia,
                p.num AS pedido_id,
                p.total - COALESCE((
                    SELECT SUM(d.importe) FROM devolucion d WHERE d.pedido = p.num
                ), 0) AS subtotal,
                z.nombre AS zona
            FROM entrega en2
            INNER JOIN pedido p ON p.entrega = en2.numero
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN zona z ON z.num = e.zona
            WHERE en2.numero = %s
        """, [entrega_id])

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        establecimientos = [dict(zip(columns, row)) for row in rows]

    if not establecimientos:
        return JsonResponse({"error": "No se encontraron establecimientos para esta entrega"}, status=404)

    return JsonResponse({
        "entrega_id": entrega_id,
        "establecimientos": establecimientos
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def calcular_ruta_entrega_coordinador(request, entrega_id):
    """
    Calcula la ruta de una entrega. Si el coordinador ya definió un orden
    en ruta_entrega_orden se respeta (usando /route/); si no, se deja que
    OSRM lo optimice (/trip/).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                e.numero AS id, e.nombre, e.latitud AS lat, e.longitud AS lon,
                e.estColonia AS colonia,
                GROUP_CONCAT(p.num ORDER BY p.num) AS pedidos,
                SUM(p.total) - COALESCE(SUM((
                    SELECT SUM(d.importe) FROM devolucion d WHERE d.pedido = p.num
                )), 0) AS subtotal,
                MIN(reo.orden) AS orden
            FROM entrega en2
            INNER JOIN pedido p ON p.entrega = en2.numero
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN ruta_entrega re ON re.entrega = en2.numero
            LEFT JOIN ruta_entrega_orden reo ON reo.ruta_entrega = re.numero
                                            AND reo.establecimiento = e.numero
            WHERE en2.numero = %s
            GROUP BY e.numero, e.nombre, e.latitud, e.longitud, e.estColonia
            ORDER BY MIN(reo.orden) IS NULL, MIN(reo.orden)
        """, [entrega_id])
        columns = [col[0] for col in cursor.description]
        establecimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if not establecimientos:
        return JsonResponse({"error": "No se encontraron establecimientos para esta entrega"}, status=404)

    tiene_orden = all(e['orden'] is not None for e in establecimientos)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (float(e["lon"]), float(e["lat"])) for e in establecimientos
    ]
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordenadas)

    try:
        if tiene_orden:
            # El coordinador ya fijó el orden: se traza tal cual
            response = requests.get(
                f"{OSRM_URL}/route/v1/driving/{coords_str}",
                params={"geometries": "geojson", "overview": "full"},
                timeout=10
            )
            data = response.json()
            if data.get("code") != "Ok":
                return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)
            trip = data["routes"][0]
            orden_final = list(range(len(coordenadas)))
        else:
            # Sin orden guardado, OSRM propone el recorrido más corto
            response = requests.get(
                f"{OSRM_URL}/trip/v1/driving/{coords_str}",
                params={
                    "roundtrip": "false", "source": "first", "destination": "last",
                    "geometries": "geojson", "overview": "full"
                },
                timeout=10
            )
            data = response.json()
            if data.get("code") != "Ok":
                return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)
            trip = data["trips"][0]
            orden_final = [wp["waypoint_index"] for wp in data["waypoints"]]
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar al servidor OSRM"}, status=500)

    paradas = []
    for i, (lon, lat) in enumerate(coordenadas):
        if i == 0:
            paradas.append({
                "lon": lon, "lat": lat, "nombre": ALMACEN["nombre"],
                "tipo": "almacen", "orden": 0
            })
        else:
            est = establecimientos[i - 1]
            paradas.append({
                "lon": lon, "lat": lat,
                "nombre": est["nombre"],
                "tipo": "establecimiento",
                "orden": orden_final[i],
                "establecimiento_id": est["id"],
                "pedido_id": est["pedidos"],
                "subtotal": float(est["subtotal"]),
                "colonia": est["colonia"]
            })

    return JsonResponse({
        "entrega_id": entrega_id,
        "distancia_total_km": round(trip["distance"] / 1000, 2),
        "duracion_total_min": round(trip["duration"] / 60, 2),
        "geometria": trip["geometry"],
        "paradas": paradas
    }, json_dumps_params={'ensure_ascii': False})


def rutas_activas(request):
    """
    Regresa todas las rutas de visita y entrega activas del día.
    """
    with connection.cursor() as cursor:
        # Rutas de visita activas
# Rutas de visita en curso: las que ya tienen ejecucion registrada
        # para hoy y todavia no se completan
        cursor.execute("""
            SELECT 
                rv.numero AS id,
                rv.nombre,
                erv.nombre AS estado,
                z.nombre AS zona,
                COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS vendedor,
                u.usuario AS vendedor_usuario,
                (SELECT COUNT(*) FROM ruta_visita_orden rvo
                  WHERE rvo.ruta_visita = rv.numero) AS total_establecimientos,
                (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                  WHERE v.ruta_visita = rv.numero
                    AND v.edo_visita IN ('EVI004','EVI005')
                    AND DATE(v.fecha) = rvs.fecha) AS completadas
            FROM ruta_visita_semana rvs
            INNER JOIN ruta_visita rv ON rv.numero = rvs.ruta_visita
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN edo_ruta_visita erv ON erv.codigo = rvs.edo_ruta_visita
            LEFT JOIN empleado em ON em.num = rvs.empleado
            LEFT JOIN usuario u ON u.empleado = em.num
            WHERE rvs.fecha = %s
              AND erv.nombre NOT IN ('Inactiva', 'Completada')
            ORDER BY rv.numero
        """, [date.today()])
        columns = [col[0] for col in cursor.description]
        rutas_visita = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Rutas de entrega activas
        # Rutas de entrega activas
        cursor.execute("""
            SELECT
                re.numero AS id,
                re.nombre,
                er.nombre AS estado,
                een.nombre AS estado_entrega,
                COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS repartidor,
                u.usuario AS repartidor_usuario,
                ve.placas AS vehiculo,
                COUNT(p.num) AS total_pedidos,
                SUM(CASE WHEN ep.nombre = 'Entregado' THEN 1 ELSE 0 END) AS entregados,
                COALESCE(SUM(p.total), 0) - COALESCE((
                    SELECT SUM(d.importe) FROM devolucion d
                    INNER JOIN pedido p2 ON p2.num = d.pedido
                    WHERE p2.entrega = en2.numero
                ), 0) AS total,
                z.nombre AS zona,
                re.entrega AS entrega_id
            FROM ruta_entrega re
            INNER JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
            LEFT JOIN empleado em ON em.num = re.empleado
            LEFT JOIN usuario u ON u.empleado = em.num
            INNER JOIN entrega en2 ON en2.numero = re.entrega
            INNER JOIN edo_entrega een ON een.codigo = en2.edo_entrega
            LEFT JOIN vehiculo ve ON ve.entrega = en2.numero
            LEFT JOIN pedido p ON p.entrega = en2.numero
            LEFT JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            LEFT JOIN visita v ON v.numero = p.visita
            LEFT JOIN establecimiento e ON e.numero = v.establecimiento
            LEFT JOIN zona z ON z.num = e.zona
            WHERE er.nombre NOT IN ('Entregada')
            GROUP BY re.numero, re.nombre, er.nombre, een.nombre,
                     em.empNombre, em.empApellPat, u.usuario,
                     ve.placas, z.nombre, re.entrega
        """)
        columns = [col[0] for col in cursor.description]
        rutas_entrega = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # Convertir Decimal a float para JSON
    for r in rutas_entrega:
        if r.get('total'):
            r['total'] = float(r['total'])

    return JsonResponse({
        "rutas_visita": rutas_visita,
        "rutas_entrega": rutas_entrega
    }, json_dumps_params={'ensure_ascii': False})


def ruta_visita_detalle(request, ruta_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                e.numero AS establecimiento_id,
                e.nombre AS establecimiento_nombre,
                e.latitud,
                e.longitud,
                e.estColonia AS colonia,
                ev.nombre AS estado_visita,
                v.numero AS visita_id,
                v.fecha,
                v.observaciones
            FROM establecimiento e
            INNER JOIN zona z ON z.num = e.zona
            INNER JOIN ruta_visita rv ON rv.zona = z.num
            LEFT JOIN visita v ON v.establecimiento = e.numero
                AND v.ruta_visita = rv.numero
                AND v.fecha = (
                    SELECT MAX(v2.fecha) 
                    FROM visita v2 
                    WHERE v2.establecimiento = e.numero 
                    AND v2.ruta_visita = rv.numero
                )
            LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita
            WHERE rv.numero = %s
            AND e.edo_establecimiento = 'EST001'
            GROUP BY e.numero, e.nombre, e.latitud, e.longitud, 
                     e.estColonia, ev.nombre, v.numero, v.fecha, v.observaciones
            ORDER BY e.nombre
        """, [ruta_id])

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        establecimientos = [dict(zip(columns, row)) for row in rows]

    return JsonResponse({
        "ruta_id": ruta_id,
        "establecimientos": establecimientos
    }, json_dumps_params={'ensure_ascii': False})
    
def rutas_visita_hoy(request):
    """
    Regresa las rutas de visita que corresponden al día de hoy
    y los vendedores disponibles para asignarles.
    """
    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    dia_hoy = dias[date.today().weekday()]

    with connection.cursor() as cursor:
        # Rutas del dia de hoy, con la ejecucion de hoy si ya se asigno
        cursor.execute("""
            SELECT
                rv.numero AS id,
                rv.nombre,
                rv.dia,
                COALESCE(erv.nombre, 'Activa') AS estado,
                z.nombre AS zona,
                COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS vendedor_asignado,
                rvs.empleado AS vendedor_id
            FROM ruta_visita rv
            INNER JOIN zona z ON z.num = rv.zona
            LEFT JOIN ruta_visita_semana rvs
                   ON rvs.ruta_visita = rv.numero AND rvs.fecha = %s
            LEFT JOIN edo_ruta_visita erv ON erv.codigo = rvs.edo_ruta_visita
            LEFT JOIN empleado em ON em.num = rvs.empleado
            WHERE rv.dia = %s
        """, [date.today(), dia_hoy])
        columns = [col[0] for col in cursor.description]
        rutas_hoy = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Vendedores activos, marcando los que ya llevan una ruta ese dia
        # Vendedores activos, marcando los que ya llevan una ruta ese dia
        cursor.execute("""
            SELECT
                em.num AS id,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS nombre,
                u.usuario,
                ede.nombre AS estado,
                (SELECT COUNT(*) FROM ruta_visita_semana rvs
                  WHERE rvs.empleado = em.num
                    AND rvs.fecha = %s
                    AND rvs.edo_ruta_visita IN ('ERV006', 'ERV003')) AS rutas_ese_dia
            FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            INNER JOIN edo_empleado ede ON ede.codigo = em.edo_empleado
            LEFT JOIN usuario u ON u.empleado = em.num
            WHERE r.nombre = 'Vendedor'
            AND ede.nombre = 'Activo'
            ORDER BY rutas_ese_dia ASC, em.empNombre
        """, [date.today()])
        columns = [col[0] for col in cursor.description]
        vendedores = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for v in vendedores:
            v['disponible'] = v['rutas_ese_dia'] == 0

    return JsonResponse({
        "dia_hoy": dia_hoy,
        "rutas_hoy": rutas_hoy,
        "vendedores_disponibles": vendedores
    }, json_dumps_params={'ensure_ascii': False})
    
@csrf_exempt
def asignar_vendedor_ruta(request, ruta_id):
    """
    Asigna un vendedor a la ruta de visita del día. Las validaciones y el
    registro los hace el procedimiento almacenado sp_asignar_vendedor_ruta:
    un vendedor no puede cubrir dos rutas la misma fecha, y una ruta ya
    asignada no se reasigna.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        vendedor_id = body.get("vendedor_id")
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not vendedor_id:
        return JsonResponse({"error": "Se requiere vendedor_id"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("SELECT dia FROM ruta_visita WHERE numero = %s", [ruta_id])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Ruta no encontrada"}, status=404)

        fecha = _fecha_de_ruta(row[0])

        try:
            cursor.callproc('sp_asignar_vendedor_ruta',
                            [ruta_id, vendedor_id, fecha])
        except Exception as e:
            mensaje = str(e)

            # El SIGNAL revierte lo que el procedimiento haya escrito, así
            # que el rechazo se registra desde aquí
            with connection.cursor() as cur2:
                cur2.execute("""
                    INSERT INTO bitacora_procedimiento
                        (procedimiento, detalle, resultado, fecha)
                    VALUES ('sp_asignar_vendedor_ruta', %s, 'RECHAZADO', NOW())
                """, [f"Ruta {ruta_id}, empleado {vendedor_id}: {mensaje[:120]}"])

            if 'ya tiene una ruta asignada' in mensaje or 'ya fue asignada' in mensaje:
                return JsonResponse({"error": mensaje}, status=409)
            return JsonResponse({"error": f"No se pudo asignar: {mensaje}"}, status=400)

    return JsonResponse({
        "mensaje": "Vendedor asignado correctamente",
        "ruta_id": ruta_id,
        "vendedor_id": vendedor_id,
        "fecha": fecha.isoformat()
    }, json_dumps_params={'ensure_ascii': False})
    
@csrf_exempt
def calcular_ruta_visita_coordinador(request, ruta_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.numero AS id, e.nombre, e.latitud AS lat, e.longitud AS lon,
                   e.estColonia AS colonia, rvo.orden
            FROM ruta_visita_orden rvo
            INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
            WHERE rvo.ruta_visita = %s ORDER BY rvo.orden
        """, [ruta_id])
        columns = [col[0] for col in cursor.description]
        establecimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]

        tiene_orden = len(establecimientos) > 0

        if not tiene_orden:
            cursor.execute("""
                SELECT DISTINCT e.numero AS id, e.nombre, e.latitud AS lat, e.longitud AS lon,
                       e.estColonia AS colonia
                FROM establecimiento e
                INNER JOIN zona z ON z.num = e.zona
                INNER JOIN ruta_visita rv ON rv.zona = z.num
                WHERE rv.numero = %s AND e.edo_establecimiento = 'EST001'
            """, [ruta_id])
            columns = [col[0] for col in cursor.description]
            establecimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if not establecimientos:
        return JsonResponse({"error": "No se encontraron establecimientos"}, status=404)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (float(e["lon"]), float(e["lat"])) for e in establecimientos
    ]
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordenadas)

    try:
        if tiene_orden:
            # Respetar el orden definido por el coordinador
            url = f"{OSRM_URL}/route/v1/driving/{coords_str}"
            response = requests.get(url, params={
                "geometries": "geojson", "overview": "full"
            }, timeout=10)
            data = response.json()
            if data.get("code") != "Ok":
                return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)
            trip = data["routes"][0]
            paradas = []
            for i, (lon, lat) in enumerate(coordenadas):
                if i == 0:
                    paradas.append({"lon": lon, "lat": lat, "nombre": ALMACEN["nombre"], "tipo": "almacen", "orden": 0})
                else:
                    est = establecimientos[i - 1]
                    paradas.append({"lon": lon, "lat": lat, "nombre": est["nombre"], "tipo": "establecimiento", "orden": i, "establecimiento_id": est["id"], "colonia": est["colonia"]})
        else:
            # Sin orden guardado, OSRM optimiza
            url = f"{OSRM_URL}/trip/v1/driving/{coords_str}"
            response = requests.get(url, params={
                "roundtrip": "false", "source": "first", "destination": "last",
                "geometries": "geojson", "overview": "full"
            }, timeout=10)
            data = response.json()
            if data.get("code") != "Ok":
                return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)
            trip = data["trips"][0]
            waypoints = data["waypoints"]
            orden_osrm = [wp["waypoint_index"] for wp in waypoints]
            paradas = []
            for i, (lon, lat) in enumerate(coordenadas):
                if i == 0:
                    paradas.append({"lon": lon, "lat": lat, "nombre": ALMACEN["nombre"], "tipo": "almacen", "orden": 0})
                else:
                    est = establecimientos[i - 1]
                    paradas.append({"lon": lon, "lat": lat, "nombre": est["nombre"], "tipo": "establecimiento", "orden": orden_osrm[i], "establecimiento_id": est["id"], "colonia": est["colonia"]})

    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar al servidor OSRM"}, status=500)

    return JsonResponse({
        "ruta_id": ruta_id,
        "distancia_total_km": round(trip["distance"] / 1000, 2),
        "duracion_total_min": round(trip["duration"] / 60, 2),
        "geometria": trip["geometry"],
        "paradas": paradas
    }, json_dumps_params={'ensure_ascii': False})

def gestionar_rutas_visita(request):
    return render(request, 'rutas/gestionar_rutas_visita.html')

def gestionar_rutas_entrega(request):
    return render(request, 'rutas/gestionar_rutas_entrega.html')

def gestionar_zonas(request):
    return render(request, 'rutas/gestionar_zonas.html')

def gestionar_establecimientos(request):
    return render(request, 'rutas/gestionar_establecimientos.html')

def rutas_visita_todas(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rv.numero AS id,
                rv.nombre,
                rv.dia,
                z.nombre AS zona,
                COALESCE(erv.nombre, 'Activa') AS estado,
                COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS vendedor,
                rvs.empleado AS vendedor_id,
                rvs.fecha,
                (SELECT COUNT(*) FROM ruta_visita_orden rvo
                  WHERE rvo.ruta_visita = rv.numero) AS total_establecimientos,
                (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                  WHERE v.ruta_visita = rv.numero
                    AND v.edo_visita IN ('EVI004','EVI005')
                    AND DATE(v.fecha) = rvs.fecha) AS completadas
            FROM ruta_visita rv
            INNER JOIN zona z ON z.num = rv.zona
            LEFT JOIN ruta_visita_semana rvs
                   ON rvs.ruta_visita = rv.numero
                  AND rvs.fecha = (
                      SELECT MAX(r2.fecha) FROM ruta_visita_semana r2
                      WHERE r2.ruta_visita = rv.numero AND r2.fecha >= %s
                  )
            LEFT JOIN edo_ruta_visita erv ON erv.codigo = rvs.edo_ruta_visita
            LEFT JOIN empleado em ON em.num = rvs.empleado
            ORDER BY rv.numero
        """, [date.today()])
        columns = [col[0] for col in cursor.description]
        rutas = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for r in rutas:
        r['fecha'] = r['fecha'].isoformat() if r.get('fecha') else None

    return JsonResponse({
        "rutas": rutas
    }, json_dumps_params={'ensure_ascii': False})
        
@csrf_exempt
def guardar_orden_ruta_entrega(request, ruta_id):
    """
    Guarda el orden de las paradas de una ruta de entrega.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        paradas = body.get("paradas", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not paradas:
        return JsonResponse({"error": "No se proporcionaron paradas"}, status=400)

    with connection.cursor() as cursor:
        # Eliminar orden anterior
        cursor.execute("DELETE FROM ruta_entrega_orden WHERE ruta_entrega = %s", [ruta_id])

        # Insertar nuevo orden
        for p in paradas:
            if p.get('tipo') == 'establecimiento':
                cursor.execute("""
                    INSERT INTO ruta_entrega_orden (ruta_entrega, establecimiento, orden)
                    VALUES (%s, %s, %s)
                """, [ruta_id, p['establecimiento_id'], p['orden']])

    return JsonResponse({
        "mensaje": "Orden guardado correctamente",
        "ruta_id": ruta_id
    }, json_dumps_params={'ensure_ascii': False})
    
def zonas(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                z.num AS id, z.nombre, z.descripcion,
                z.lat_min, z.lat_max, z.lon_min, z.lon_max,
                z.poligono,
                COUNT(e.numero) AS total_establecimientos
            FROM zona z
            LEFT JOIN establecimiento e ON e.zona = z.num
            GROUP BY z.num, z.nombre, z.descripcion, z.lat_min, z.lat_max,
                     z.lon_min, z.lon_max, z.poligono
            ORDER BY z.num
        """)
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for r in result:
        for campo in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
            if r[campo] is not None:
                r[campo] = float(r[campo])
        # El contorno se guarda como JSON: se devuelve ya convertido
        if r.get('poligono'):
            r['poligono'] = json.loads(r['poligono'])

    return JsonResponse({"zonas": result}, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def actualizar_zona(request, zona_id):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE zona SET
                lat_min = %s, lat_max = %s,
                lon_min = %s, lon_max = %s
            WHERE num = %s
        """, [
            body.get('lat_min'), body.get('lat_max'),
            body.get('lon_min'), body.get('lon_max'),
            zona_id
        ])

    return JsonResponse({"mensaje": "Zona actualizada correctamente"}, json_dumps_params={'ensure_ascii': False})

def establecimientos(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                establecimiento_id AS id,
                establecimiento_nombre AS nombre,
                colonia,
                telefono,
                latitud,
                longitud,
                zona_id,
                zona_nombre,
                estado_establecimiento AS estado
            FROM vta_establecimientos_por_zona
            ORDER BY zona_nombre, establecimiento_nombre
        """)
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for r in result:
        for campo in ['latitud', 'longitud']:
            if r[campo] is not None:
                r[campo] = float(r[campo])

    return JsonResponse({"establecimientos": result}, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def actualizar_establecimiento(request, est_id):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE establecimiento
            SET zona = %s, edo_establecimiento = %s
            WHERE numero = %s
        """, [body.get('zona'), body.get('estado'), est_id])

    return JsonResponse({"mensaje": "Establecimiento actualizado"}, json_dumps_params={'ensure_ascii': False})


DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']


def _dias_contiguos(dia):
    """
    Devuelve el día anterior, el mismo y el siguiente. Un establecimiento
    no debe recibir visita en días consecutivos: se atiende una vez por
    semana y hay que dejar margen entre recorridos.
    """
    if dia not in DIAS_SEMANA:
        return [dia]
    i = DIAS_SEMANA.index(dia)
    dias = [dia]
    if i > 0:
        dias.append(DIAS_SEMANA[i - 1])
    if i < len(DIAS_SEMANA) - 1:
        dias.append(DIAS_SEMANA[i + 1])
    return dias


def _establecimientos_ocupados(cursor, dia, establecimientos, ruta_excluir=None):
    """
    De la lista dada, devuelve los que ya están en otra ruta de visita
    programada para un día contiguo. Ahora que la ruta es una plantilla
    permanente, basta con revisar el día: si existe la ruta, el
    establecimiento se visita ese día todas las semanas.
    """
    if not establecimientos:
        return []

    dias = _dias_contiguos(dia)
    marcas_dias = ','.join(['%s'] * len(dias))
    marcas_est = ','.join(['%s'] * len(establecimientos))

    sql = f"""
        SELECT DISTINCT e.nombre, rv.nombre AS ruta, rv.dia
        FROM ruta_visita_orden rvo
        INNER JOIN ruta_visita rv ON rv.numero = rvo.ruta_visita
        INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
        WHERE rvo.establecimiento IN ({marcas_est})
          AND rv.dia IN ({marcas_dias})
    """
    params = list(establecimientos) + dias

    if ruta_excluir:
        sql += " AND rv.numero <> %s"
        params.append(ruta_excluir)

    cursor.execute(sql, params)
    return [{"establecimiento": r[0], "ruta": r[1], "dia": r[2]} for r in cursor.fetchall()]

@csrf_exempt
def crear_ruta_visita(request):
    """
    Crea una ruta de visita con sus paradas. El trigger
    tg_establecimiento_una_sola_ruta valida que ningún establecimiento
    pertenezca ya a otra ruta; los que se rechacen se reportan sin
    tumbar la creación de la ruta.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    nombre = body.get('nombre')
    dia = body.get('dia')
    descripcion = body.get('descripcion', '')
    zona_id = body.get('zona_id')
    establecimientos = body.get('establecimientos', [])

    if not nombre or not dia or not zona_id:
        return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

    rechazados = []

    with connection.cursor() as cursor:
        # La ruta nace sin vendedor: el coordinador lo asigna cada semana
        # y ese registro vive en ruta_visita_semana
        cursor.execute("""
            INSERT INTO ruta_visita (nombre, descripcion, dia, zona)
            VALUES (%s, %s, %s, %s)
        """, [nombre, descripcion, dia, zona_id])
        nuevo_num = cursor.lastrowid

    # Cada parada se inserta por separado para que un establecimiento
    # rechazado por el trigger no impida agregar los demás
    for i, est_id in enumerate(establecimientos):
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ruta_visita_orden (ruta_visita, establecimiento, orden)
                        VALUES (%s, %s, %s)
                    """, [nuevo_num, est_id, i + 1])
        except Exception as e:
            rechazados.append({"establecimiento": est_id, "motivo": str(e)})
            # El SIGNAL revierte el registro que hace el trigger, así que
            # el rechazo se deja desde aquí
            with connection.cursor() as cur2:
                cur2.execute("""
                    INSERT INTO bitacora_trigger (trigger_nombre, detalle, fecha)
                    VALUES ('tg_establecimiento_una_sola_ruta', %s, NOW())
                """, [f"Establecimiento {est_id} RECHAZADO en ruta {nuevo_num}: {str(e)[:120]}"])

    


    # Si ninguna parada pudo entrar, la ruta quedaria vacia y no sirve
    if establecimientos and len(rechazados) == len(establecimientos):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ruta_visita WHERE numero = %s", [nuevo_num])
        return JsonResponse({
            "error": "Ningún establecimiento pudo agregarse: todos pertenecen ya a otra ruta",
            "establecimientos_rechazados": rechazados
        }, status=409)

    return JsonResponse({
        "mensaje": "Ruta creada correctamente",
        "ruta_id": nuevo_num,
        "establecimientos_rechazados": rechazados
    }, json_dumps_params={'ensure_ascii': False})
    
    
def ruta_visita_datos(request, ruta_id):
    """
    Regresa los datos de una ruta de visita para edición. El estado y el
    vendedor salen de la ejecución vigente; si la ruta todavía no se ha
    asignado esta semana, se reporta como Activa.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rv.numero AS id, rv.nombre, rv.dia, rv.descripcion,
                   rv.zona AS zona_id, z.nombre AS zona_nombre,
                   COALESCE(erv.nombre, 'Activa') AS estado,
                   rvs.empleado AS vendedor_id
            FROM ruta_visita rv
            INNER JOIN zona z ON z.num = rv.zona
            LEFT JOIN ruta_visita_semana rvs
                   ON rvs.ruta_visita = rv.numero
                  AND rvs.fecha = (
                      SELECT MAX(r2.fecha) FROM ruta_visita_semana r2
                      WHERE r2.ruta_visita = rv.numero AND r2.fecha >= %s
                  )
            LEFT JOIN edo_ruta_visita erv ON erv.codigo = rvs.edo_ruta_visita
            WHERE rv.numero = %s
        """, [date.today(), ruta_id])
        columns = [col[0] for col in cursor.description]
        fila = cursor.fetchone()
        if not fila:
            return JsonResponse({"error": "Ruta no encontrada"}, status=404)
        ruta = dict(zip(columns, fila))

        # Obtener establecimientos en orden
        cursor.execute("""
            SELECT e.numero AS id, e.nombre, e.latitud, e.longitud,
                   e.estColonia AS colonia, rvo.orden
            FROM ruta_visita_orden rvo
            INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
            WHERE rvo.ruta_visita = %s
            ORDER BY rvo.orden
        """, [ruta_id])
        columns = [col[0] for col in cursor.description]
        establecimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for e in establecimientos:
            e['latitud'] = float(e['latitud']) if e['latitud'] else None
            e['longitud'] = float(e['longitud']) if e['longitud'] else None

    return JsonResponse({
        "ruta": ruta,
        "establecimientos": establecimientos
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def editar_ruta_visita(request, ruta_id):
    """
    Edita una ruta de visita existente.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    nombre = body.get('nombre')
    dia = body.get('dia')
    descripcion = body.get('descripcion', '')
    zona_id = body.get('zona_id')
    establecimientos = body.get('establecimientos', [])

    if not nombre or not dia or not zona_id:
        return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE ruta_visita SET nombre=%s, dia=%s, descripcion=%s, zona=%s
            WHERE numero=%s
        """, [nombre, dia, descripcion, zona_id, ruta_id])

        # Actualizar orden
        cursor.execute("DELETE FROM ruta_visita_orden WHERE ruta_visita = %s", [ruta_id])
        for i, est_id in enumerate(establecimientos):
            cursor.execute("""
                INSERT INTO ruta_visita_orden (ruta_visita, establecimiento, orden)
                VALUES (%s, %s, %s)
            """, [ruta_id, est_id, i + 1])

    return JsonResponse({
        "mensaje": "Ruta actualizada correctamente",
        "ruta_id": ruta_id
    }, json_dumps_params={'ensure_ascii': False})
    
def historial_rutas(request):
    """
    Historial unificado de rutas de visita y de entrega, con filtros
    por tipo, estado y responsable. En las de visita cada fila es una
    ejecución semanal, así queda registro de quién llevó la ruta cada
    semana. El detalle de paradas se pide aparte para no cargar todo
    de golpe.
    """
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    empleado = request.GET.get('empleado', '')

    rutas_visita = []
    rutas_entrega = []

    with connection.cursor() as cursor:
        if tipo in ('', 'visita'):
            sql = """
                SELECT rvs.numero AS ejecucion_id,
                       rv.numero AS id, rv.nombre, rv.dia,
                       rvs.fecha,
                       erv.nombre AS estado, z.nombre AS zona,
                       COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS responsable,
                       em.num AS responsable_id,
                       (SELECT COUNT(*) FROM ruta_visita_orden rvo
                         WHERE rvo.ruta_visita = rv.numero) AS total_paradas,
                       (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                         WHERE v.ruta_visita = rv.numero
                           AND v.edo_visita IN ('EVI004','EVI005')
                           AND DATE(v.fecha) = rvs.fecha) AS completadas,
                       (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                         WHERE v.ruta_visita = rv.numero
                           AND v.edo_visita = 'EVI005'
                           AND DATE(v.fecha) = rvs.fecha) AS sin_pedido,
                       (SELECT MAX(v.fecha) FROM visita v
                         WHERE v.ruta_visita = rv.numero
                           AND DATE(v.fecha) = rvs.fecha) AS ultima_actividad
                FROM ruta_visita_semana rvs
                INNER JOIN ruta_visita rv ON rv.numero = rvs.ruta_visita
                INNER JOIN edo_ruta_visita erv ON erv.codigo = rvs.edo_ruta_visita
                INNER JOIN zona z ON z.num = rv.zona
                LEFT JOIN empleado em ON em.num = rvs.empleado
                WHERE 1 = 1
            """
            params = []
            if estado:
                sql += " AND erv.nombre = %s"
                params.append(estado)
            if empleado:
                sql += " AND rvs.empleado = %s"
                params.append(empleado)
            sql += " ORDER BY rvs.fecha DESC, rv.numero"

            cursor.execute(sql, params)
            columns = [c[0] for c in cursor.description]
            rutas_visita = [dict(zip(columns, r)) for r in cursor.fetchall()]

        if tipo in ('', 'entrega'):
            sql = """
                SELECT re.numero AS id, re.nombre,
                       ere.nombre AS estado,
                       en.numero AS entrega_id, en.fecha_creacion, en.fecha_entrega,
                       COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS responsable,
                       em.num AS responsable_id,
                       veh.placas,
                       COUNT(DISTINCT p.num) AS total_paradas,
                       SUM(CASE WHEN ep.nombre = 'Entregado' THEN 1 ELSE 0 END) AS completadas,
                       COALESCE(SUM(p.total), 0) - COALESCE(SUM((
                           SELECT SUM(d.importe) FROM devolucion d WHERE d.pedido = p.num
                       )), 0) AS monto
                FROM ruta_entrega re
                INNER JOIN edo_ruta_entrega ere ON ere.codigo = re.edo_ruta_entrega
                INNER JOIN entrega en ON en.numero = re.entrega
                LEFT JOIN empleado em ON em.num = re.empleado
                LEFT JOIN vehiculo veh ON veh.entrega = en.numero
                LEFT JOIN pedido p ON p.entrega = en.numero
                LEFT JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
                WHERE 1 = 1
            """
            params = []
            if estado:
                sql += " AND ere.nombre = %s"
                params.append(estado)
            if empleado:
                sql += " AND re.empleado = %s"
                params.append(empleado)
            sql += """
                GROUP BY re.numero, re.nombre, ere.nombre, en.numero,
                         en.fecha_creacion, en.fecha_entrega,
                         em.empNombre, em.empApellPat, em.num, veh.placas
                ORDER BY re.numero DESC
            """
            cursor.execute(sql, params)
            columns = [c[0] for c in cursor.description]
            rutas_entrega = [dict(zip(columns, r)) for r in cursor.fetchall()]

        # Responsables para el filtro (siempre la lista completa)
        cursor.execute("""
            SELECT em.num AS id,
                   CONCAT(em.empNombre, ' ', em.empApellPat) AS nombre,
                   r.nombre AS rol
            FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            WHERE r.nombre IN ('Vendedor', 'Repartidor')
            ORDER BY r.nombre, em.empNombre
        """)
        columns = [c[0] for c in cursor.description]
        responsables = [dict(zip(columns, r)) for r in cursor.fetchall()]

    for r in rutas_entrega:
        r['monto'] = float(r['monto'] or 0)
        r['fecha_creacion'] = r['fecha_creacion'].isoformat() if r['fecha_creacion'] else None
        r['fecha_entrega'] = r['fecha_entrega'].isoformat() if r['fecha_entrega'] else None

    for r in rutas_visita:
        r['fecha'] = r['fecha'].isoformat() if r.get('fecha') else None
        r['ultima_actividad'] = r['ultima_actividad'].isoformat() if r['ultima_actividad'] else None

    return JsonResponse({
        "rutas_visita": rutas_visita,
        "rutas_entrega": rutas_entrega,
        "responsables": responsables
    }, json_dumps_params={'ensure_ascii': False})


def paradas_ruta_visita(request, ruta_id):
    """Paradas de una ruta de visita con el resultado de cada una."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rvo.orden, e.numero AS establecimiento_id, e.nombre,
                   e.estColonia AS colonia,
                   COALESCE(ev.nombre, 'Pendiente') AS estado_visita,
                   v.fecha, v.observaciones,
                   p.num AS pedido_id,
                   p.total - COALESCE((
                       SELECT SUM(d.importe) FROM devolucion d WHERE d.pedido = p.num
                   ), 0) AS total
            FROM ruta_visita_orden rvo
            INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
            LEFT JOIN visita v ON v.ruta_visita = rvo.ruta_visita
                              AND v.establecimiento = rvo.establecimiento
            LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita
            LEFT JOIN pedido p ON p.visita = v.numero
            WHERE rvo.ruta_visita = %s
            ORDER BY rvo.orden
        """, [ruta_id])
        columns = [c[0] for c in cursor.description]
        paradas = [dict(zip(columns, r)) for r in cursor.fetchall()]

    for p in paradas:
        p['total'] = float(p['total']) if p['total'] else None
        p['fecha'] = p['fecha'].isoformat() if p['fecha'] else None

    return JsonResponse({"paradas": paradas}, json_dumps_params={'ensure_ascii': False})


def paradas_ruta_entrega(request, ruta_id):
    """Paradas de una ruta de entrega con su confirmación."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(reo.orden, 999) AS orden,
                   e.numero AS establecimiento_id, e.nombre,
                   e.estColonia AS colonia,
                   p.num AS pedido_id,
                   p.total - COALESCE((
                       SELECT SUM(d.importe) FROM devolucion d WHERE d.pedido = p.num
                   ), 0) AS total
                   ep.nombre AS estado_pedido,
                   ee.fecha_entrega, ee.hora_entrega
            FROM ruta_entrega re
            INNER JOIN entrega en ON en.numero = re.entrega
            INNER JOIN pedido p ON p.entrega = en.numero
            INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            LEFT JOIN ruta_entrega_orden reo ON reo.ruta_entrega = re.numero
                                            AND reo.establecimiento = e.numero
            LEFT JOIN entrega_estable ee ON ee.entrega = en.numero
                                        AND ee.establecimiento = e.numero
            WHERE re.numero = %s
            ORDER BY orden
        """, [ruta_id])
        columns = [c[0] for c in cursor.description]
        paradas = [dict(zip(columns, r)) for r in cursor.fetchall()]

    for p in paradas:
        p['subtotal'] = float(p['subtotal']) if p['subtotal'] else 0
        p['fecha_entrega'] = p['fecha_entrega'].isoformat() if p['fecha_entrega'] else None
        p['hora_entrega'] = str(p['hora_entrega']) if p['hora_entrega'] else None

    return JsonResponse({"paradas": paradas}, json_dumps_params={'ensure_ascii': False})


def historial_rutas_view(request):
    return render(request, 'rutas/historial_rutas.html')

def repartidores_disponibles(request):
    """
    RF32: repartidores activos con la carga de trabajo que traen hoy,
    para que el coordinador decida a quién asignarle una ruta.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT em.num AS id,
                   CONCAT(em.empNombre, ' ', em.empApellPat) AS nombre,
                   u.usuario,
                   (SELECT COUNT(*) FROM ruta_entrega re
                     WHERE re.empleado = em.num
                       AND re.edo_ruta_entrega IN ('ERET001','ERET002')) AS rutas_activas
            FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            INNER JOIN edo_empleado ee ON ee.codigo = em.edo_empleado
            LEFT JOIN usuario u ON u.empleado = em.num
            WHERE r.nombre = 'Repartidor' AND ee.nombre = 'Activo'
            ORDER BY rutas_activas ASC, em.empNombre
        """)
        columns = [c[0] for c in cursor.description]
        repartidores = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for r in repartidores:
        r['disponible'] = r['rutas_activas'] == 0

    return JsonResponse({"repartidores": repartidores},
                        json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def aprobar_ruta_entrega(request, ruta_id):
    """
    RF30 + RF33: el coordinador revisa la ruta que armó el almacenista,
    le pone nombre y descripción, y la libera para los repartidores
    (entrega Creada -> Cargada). Puede asignarla a un repartidor
    específico o dejarla disponible para que la tome cualquiera.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    nombre = (body.get('nombre') or '').strip()
    descripcion = (body.get('descripcion') or '').strip() or None
    repartidor_id = body.get('repartidor_id') or None

    if not nombre:
        return JsonResponse({"error": "El nombre de la ruta es requerido"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT re.entrega, en.edo_entrega
            FROM ruta_entrega re
            INNER JOIN entrega en ON en.numero = re.entrega
            WHERE re.numero = %s
        """, [ruta_id])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Ruta no encontrada"}, status=404)

        entrega_id, edo_actual = row
        if edo_actual != 'EEN001':
            return JsonResponse({"error": "Esta ruta ya fue liberada"}, status=409)

        # Un repartidor solo puede llevar una ruta a la vez: una entrega
        # equivale a un camión y no puede manejar dos al mismo tiempo
        if repartidor_id:
            cursor.execute("""
                SELECT COUNT(*) FROM ruta_entrega
                WHERE empleado = %s AND edo_ruta_entrega IN ('ERET001','ERET002')
            """, [repartidor_id])
            if cursor.fetchone()[0] > 0:
                return JsonResponse({
                    "error": "Ese repartidor ya tiene una ruta activa"
                }, status=409)

        cursor.execute("""
            UPDATE ruta_entrega SET nombre = %s, descripcion = %s, empleado = %s
            WHERE numero = %s
        """, [nombre, descripcion, repartidor_id, ruta_id])

        cursor.execute("""
            UPDATE entrega SET edo_entrega = 'EEN003' WHERE numero = %s
        """, [entrega_id])

    return JsonResponse({
        "mensaje": "Ruta liberada correctamente",
        "ruta_id": ruta_id,
        "asignada": bool(repartidor_id)
    }, json_dumps_params={'ensure_ascii': False})
    
@csrf_exempt
def trazar_ruta_orden(request):
    """
    Traza la ruta respetando el orden exacto de los puntos recibidos.
    A diferencia de calcular_ruta_entrega (que usa /trip/ y reoptimiza),
    aquí se usa /route/ porque el orden ya lo definió el coordinador.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        establecimientos = body.get("establecimientos", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not establecimientos:
        return JsonResponse({"error": "No se proporcionaron establecimientos"}, status=400)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (float(e["lon"]), float(e["lat"])) for e in establecimientos
    ]
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordenadas)

    try:
        response = requests.get(
            f"{OSRM_URL}/route/v1/driving/{coords_str}",
            params={"geometries": "geojson", "overview": "full"},
            timeout=10
        )
        data = response.json()
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar al servidor OSRM"}, status=500)

    if data.get("code") != "Ok":
        return JsonResponse({"error": "OSRM no pudo calcular la ruta"}, status=400)

    ruta = data["routes"][0]
    return JsonResponse({
        "distancia_total_km": round(ruta["distance"] / 1000, 2),
        "duracion_total_min": round(ruta["duration"] / 60, 2),
        "geometria": ruta["geometry"]
    }, json_dumps_params={'ensure_ascii': False})
    
@csrf_exempt
def guardar_poligono_zona(request, zona_id):
    """
    Guarda el contorno que el coordinador dibujó sobre el mapa. Es solo
    para visualización: los límites que determinan a qué zona pertenece
    un establecimiento siguen siendo lat_min/lat_max/lon_min/lon_max.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        puntos = json.loads(request.body).get('puntos')
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # Un contorno vacío borra el dibujo y devuelve la zona a su rectángulo
    valor = json.dumps(puntos) if puntos and len(puntos) >= 3 else None

    with connection.cursor() as cursor:
        cursor.execute("UPDATE zona SET poligono = %s WHERE num = %s", [valor, zona_id])
        if cursor.rowcount == 0:
            return JsonResponse({"error": "Zona no encontrada"}, status=404)

    return JsonResponse({"mensaje": "Contorno guardado", "zona_id": zona_id})

def _fecha_de_ruta(dia):
    """
    Fecha en que corre la ruta de ese día de la semana. Se toma la
    ocurrencia de la semana en curso; si ya pasó, la de la siguiente.
    Así el coordinador puede asignar con anticipación sin elegir fecha.
    """
    
    if dia not in DIAS_SEMANA:
        return date.today()

    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    fecha = lunes + timedelta(days=DIAS_SEMANA.index(dia))
    if fecha < hoy:
        fecha += timedelta(days=7)
    return fecha


def establecimientos_sin_ruta(request):
    """
    Establecimientos que ya existen pero no pertenecen a ninguna ruta de
    visita. Sin ruta nadie los visita, asi que el coordinador necesita
    verlos para asignarlos.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.numero AS id, e.nombre, e.zona,
                   z.nombre AS zona_nombre,
                   e.estColonia AS colonia,
                   e.latitud, e.longitud,
                   e.fecha_registro
            FROM establecimiento e
            INNER JOIN zona z ON z.num = e.zona
            WHERE NOT EXISTS (
                SELECT 1 FROM ruta_visita_orden rvo
                WHERE rvo.establecimiento = e.numero
            )
            ORDER BY e.zona, e.numero
        """)
        columns = [c[0] for c in cursor.description]
        establecimientos = [dict(zip(columns, r)) for r in cursor.fetchall()]

    for e in establecimientos:
        e['latitud'] = float(e['latitud']) if e['latitud'] else None
        e['longitud'] = float(e['longitud']) if e['longitud'] else None
        e['fecha_registro'] = e['fecha_registro'].isoformat() if e['fecha_registro'] else None

    return JsonResponse({
        "total": len(establecimientos),
        "establecimientos": establecimientos
    }, json_dumps_params={'ensure_ascii': False})