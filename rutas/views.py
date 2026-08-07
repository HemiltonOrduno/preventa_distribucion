import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from usuarios.permissions import rol_requerido

# Coordenadas del almacén (Pepsico El Florido, Tijuana)
ALMACEN = {
    "lon": -116.9400,
    "lat": 32.4700,
    "nombre": "Almacén Sabritas - El Florido"
}

OSRM_URL = "http://127.0.0.1:5000"

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
                p.total AS subtotal,
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
                SUM(p.total) AS subtotal,
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
        cursor.execute("""
            SELECT 
                rv.numero AS id,
                rv.nombre,
                erv.nombre AS estado,
                z.nombre AS zona,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor,
                COUNT(v.numero) AS total_establecimientos,
                SUM(CASE WHEN ev.nombre IN ('Completada', 'Completada sin pedido') THEN 1 ELSE 0 END) AS completadas
            FROM ruta_visita rv
            INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN empleado em ON em.num = rv.empleado
            LEFT JOIN visita v ON v.ruta_visita = rv.numero
            LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita
            WHERE erv.nombre NOT IN ('Inactiva', 'Completada')
            GROUP BY rv.numero, rv.nombre, erv.nombre, z.nombre, em.empNombre, em.empApellPat
        """)
        columns = [col[0] for col in cursor.description]
        rutas_visita = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Rutas de entrega activas
        cursor.execute("""
            SELECT 
                re.numero AS id,
                re.nombre,
                er.nombre AS estado,
                een.nombre AS estado_entrega,
                COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS repartidor,
                ve.placas AS vehiculo,
                COUNT(p.num) AS total_pedidos,
                SUM(CASE WHEN ep.nombre = 'Entregado' THEN 1 ELSE 0 END) AS entregados,
                COALESCE(SUM(p.total), 0) AS total,
                z.nombre AS zona,
                re.entrega AS entrega_id
            FROM ruta_entrega re
            INNER JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
            LEFT JOIN empleado em ON em.num = re.empleado
            INNER JOIN entrega en2 ON en2.numero = re.entrega
            INNER JOIN edo_entrega een ON een.codigo = en2.edo_entrega
            LEFT JOIN vehiculo ve ON ve.entrega = en2.numero
            LEFT JOIN pedido p ON p.entrega = en2.numero
            LEFT JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            LEFT JOIN visita v ON v.numero = p.visita
            LEFT JOIN establecimiento e ON e.numero = v.establecimiento
            LEFT JOIN zona z ON z.num = e.zona
            WHERE er.nombre NOT IN ('Entregada')
            GROUP BY re.numero, re.nombre, er.nombre, een.nombre, em.empNombre, em.empApellPat, ve.placas, z.nombre, re.entrega
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
    from datetime import date
    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    dia_hoy = dias[date.today().weekday()]

    with connection.cursor() as cursor:
        # Rutas del día de hoy
        cursor.execute("""
            SELECT
                rv.numero AS id,
                rv.nombre,
                rv.dia,
                erv.nombre AS estado,
                z.nombre AS zona,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor_asignado,
                em.num AS vendedor_id
            FROM ruta_visita rv
            INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN empleado em ON em.num = rv.empleado
            WHERE rv.dia = %s AND erv.nombre = 'Activa'
        """, [dia_hoy])
        columns = [col[0] for col in cursor.description]
        rutas_hoy = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Vendedores disponibles
        cursor.execute("""
            SELECT
                em.num AS id,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS nombre,
                ede.nombre AS estado
            FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            INNER JOIN edo_empleado ede ON ede.codigo = em.edo_empleado
            WHERE r.nombre = 'Vendedor'
            AND ede.nombre = 'Activo'
        """)
        columns = [col[0] for col in cursor.description]
        vendedores = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({
        "dia_hoy": dia_hoy,
        "rutas_hoy": rutas_hoy,
        "vendedores_disponibles": vendedores
    }, json_dumps_params={'ensure_ascii': False})
    
@csrf_exempt
def asignar_vendedor_ruta(request, ruta_id):
    """
    Asigna un vendedor a una ruta de visita y la marca como Asignada.
    Solo se puede asignar si la ruta está Activa (no si ya fue asignada).
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
        cursor.execute("""
            UPDATE ruta_visita
            SET empleado = %s, edo_ruta_visita = 'ERV006'
            WHERE numero = %s AND edo_ruta_visita = 'ERV001'
        """, [vendedor_id, ruta_id])

        if cursor.rowcount == 0:
            return JsonResponse({"error": "La ruta ya fue asignada o no está activa"}, status=409)

    return JsonResponse({
        "mensaje": "Vendedor asignado correctamente",
        "ruta_id": ruta_id,
        "vendedor_id": vendedor_id
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
                erv.nombre AS estado,
                z.nombre AS zona,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor_asignado,
                em.num AS vendedor_id,
                COUNT(v.numero) AS total_establecimientos,
                SUM(CASE WHEN ev.nombre IN ('Completada', 'Completada sin pedido') THEN 1 ELSE 0 END) AS completadas
            FROM ruta_visita rv
            INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN empleado em ON em.num = rv.empleado
            LEFT JOIN visita v ON v.ruta_visita = rv.numero
            LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita
            WHERE erv.nombre != 'Inactiva'
            GROUP BY rv.numero, rv.nombre, rv.dia, erv.nombre, z.nombre, em.empNombre, em.empApellPat, em.num
            ORDER BY rv.dia, rv.numero
        """)
        columns = [col[0] for col in cursor.description]
        rutas = [dict(zip(columns, row)) for row in cursor.fetchall()]

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
                z.num AS id,
                z.nombre,
                z.descripcion,
                z.lat_min, z.lat_max,
                z.lon_min, z.lon_max,
                COUNT(e.numero) AS total_establecimientos
            FROM zona z
            LEFT JOIN establecimiento e ON e.zona = z.num
            GROUP BY z.num, z.nombre, z.descripcion, z.lat_min, z.lat_max, z.lon_min, z.lon_max
            ORDER BY z.num
        """)
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for r in result:
        for campo in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
            if r[campo] is not None:
                r[campo] = float(r[campo])

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

@csrf_exempt
def crear_ruta_visita(request):
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
        cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM ruta_visita")
        nuevo_num = cursor.fetchone()[0]

        cursor.execute("""
            SELECT em.num FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            WHERE r.nombre = 'Vendedor'
            AND em.edo_empleado = 'EE001'
            LIMIT 1
        """)
        vendedor = cursor.fetchone()
        vendedor_id = vendedor[0] if vendedor else None

        cursor.execute("""
            INSERT INTO ruta_visita (numero, nombre, descripcion, dia, zona, empleado, edo_ruta_visita)
            VALUES (%s, %s, %s, %s, %s, %s, 'ERV001')
        """, [nuevo_num, nombre, descripcion, dia, zona_id, vendedor_id])

        # Guardar orden en ruta_visita_orden
        for i, est_id in enumerate(establecimientos):
            cursor.execute("""
                INSERT INTO ruta_visita_orden (ruta_visita, establecimiento, orden)
                VALUES (%s, %s, %s)
            """, [nuevo_num, est_id, i + 1])

    return JsonResponse({
        "mensaje": "Ruta creada correctamente",
        "ruta_id": nuevo_num
    }, json_dumps_params={'ensure_ascii': False})
    
    
def ruta_visita_datos(request, ruta_id):
    """
    Regresa los datos de una ruta de visita para edición.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rv.numero AS id, rv.nombre, rv.dia, rv.descripcion,
                   rv.zona AS zona_id, z.nombre AS zona_nombre,
                   erv.nombre AS estado, rv.empleado AS vendedor_id
            FROM ruta_visita rv
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
            WHERE rv.numero = %s
        """, [ruta_id])
        columns = [col[0] for col in cursor.description]
        ruta = dict(zip(columns, cursor.fetchone()))

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
    por tipo, estado y responsable. El detalle de paradas se pide
    aparte para no cargar todo de golpe.
    """
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    empleado = request.GET.get('empleado', '')

    rutas_visita = []
    rutas_entrega = []

    with connection.cursor() as cursor:
        if tipo in ('', 'visita'):
            sql = """
                SELECT rv.numero AS id, rv.nombre, rv.dia,
                       erv.nombre AS estado, z.nombre AS zona,
                       COALESCE(CONCAT(em.empNombre, ' ', em.empApellPat), 'Sin asignar') AS responsable,
                       em.num AS responsable_id,
                       (SELECT COUNT(*) FROM ruta_visita_orden rvo
                         WHERE rvo.ruta_visita = rv.numero) AS total_paradas,
                       (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                         WHERE v.ruta_visita = rv.numero
                           AND v.edo_visita IN ('EVI004','EVI005')) AS completadas,
                       (SELECT COUNT(DISTINCT v.establecimiento) FROM visita v
                         WHERE v.ruta_visita = rv.numero
                           AND v.edo_visita = 'EVI005') AS sin_pedido,
                       (SELECT MAX(v.fecha) FROM visita v
                         WHERE v.ruta_visita = rv.numero) AS ultima_actividad
                FROM ruta_visita rv
                INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
                INNER JOIN zona z ON z.num = rv.zona
                LEFT JOIN empleado em ON em.num = rv.empleado
                WHERE 1 = 1
            """
            params = []
            if estado:
                sql += " AND erv.nombre = %s"
                params.append(estado)
            if empleado:
                sql += " AND rv.empleado = %s"
                params.append(empleado)
            sql += " ORDER BY rv.numero DESC"

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
                       COALESCE(SUM(p.total), 0) AS monto
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
                   p.num AS pedido_id, p.total
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
                   p.num AS pedido_id, p.total AS subtotal,
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
                   (SELECT COUNT(*) FROM ruta_entrega re
                     WHERE re.empleado = em.num
                       AND re.edo_ruta_entrega IN ('ERET001','ERET002')) AS rutas_activas
            FROM empleado em
            INNER JOIN rol r ON r.codigo = em.rol
            INNER JOIN edo_empleado ee ON ee.codigo = em.edo_empleado
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