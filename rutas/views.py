import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# Coordenadas del almacén (Pepsico El Florido, Tijuana)
ALMACEN = {
    "lon": -116.9400,
    "lat": 32.4700,
    "nombre": "Almacén Sabritas - El Florido"
}

OSRM_URL = "http://127.0.0.1:5000"


def mapa(request):
    return render(request, "rutas/mapa.html")


def coordinador(request):
    return render(request, "rutas/coordinador.html")


@csrf_exempt
def calcular_ruta_visita(request):
    """
    Calcula la ruta óptima de visita para un vendedor.
    Recibe una lista de establecimientos y regresa la ruta optimizada.
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
                "establecimiento_id": est.get("id")
            })

    return JsonResponse({
        "distancia_total_km": round(trip["distance"] / 1000, 2),
        "duracion_total_min": round(trip["duration"] / 60, 2),
        "geometria": trip["geometry"],
        "paradas": paradas
    }, json_dumps_params={'ensure_ascii': False})


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
                p.subtotal,
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
    Calcula la ruta óptima para una entrega específica.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.numero AS id,
                e.nombre AS nombre,
                e.latitud AS lat,
                e.longitud AS lon,
                p.num AS pedido_id,
                p.subtotal,
                e.estColonia AS colonia
            FROM entrega en2
            INNER JOIN pedido p ON p.entrega = en2.numero
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            WHERE en2.numero = %s
        """, [entrega_id])

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        establecimientos = [dict(zip(columns, row)) for row in rows]

    if not establecimientos:
        return JsonResponse({"error": "No se encontraron establecimientos para esta entrega"}, status=404)

    coordenadas = [(ALMACEN["lon"], ALMACEN["lat"])] + [
        (float(e["lon"]), float(e["lat"])) for e in establecimientos
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
                "nombre": est["nombre"],
                "tipo": "establecimiento",
                "orden": orden[i],
                "establecimiento_id": est["id"],
                "pedido_id": est["pedido_id"],
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
                CONCAT(em.empNombre, ' ', em.empApellPat) AS repartidor,
                ve.placas AS vehiculo,
                COUNT(p.num) AS total_pedidos,
                SUM(CASE WHEN ep.nombre = 'Entregado' THEN 1 ELSE 0 END) AS entregados,
                COALESCE(SUM(p.total), 0) AS total,
                z.nombre AS zona,
                re.entrega AS entrega_id
            FROM ruta_entrega re
            INNER JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
            INNER JOIN empleado em ON em.num = re.empleado
            INNER JOIN entrega en2 ON en2.numero = re.entrega
            LEFT JOIN vehiculo ve ON ve.entrega = en2.numero
            LEFT JOIN pedido p ON p.entrega = en2.numero
            LEFT JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            LEFT JOIN visita v ON v.numero = p.visita
            LEFT JOIN establecimiento e ON e.numero = v.establecimiento
            LEFT JOIN zona z ON z.num = e.zona
            WHERE er.nombre NOT IN ('Entregada')
            GROUP BY re.numero, re.nombre, er.nombre, em.empNombre, em.empApellPat, ve.placas, z.nombre, re.entrega
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
    """
    Regresa los establecimientos de una ruta de visita con sus estados.
    """
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
            FROM ruta_visita rv
            INNER JOIN zona z ON z.num = rv.zona
            INNER JOIN establecimiento e ON e.zona = z.num
            LEFT JOIN visita v ON v.establecimiento = e.numero AND v.ruta_visita = rv.numero
            LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita
            WHERE rv.numero = %s
            ORDER BY ev.nombre DESC
        """, [ruta_id])

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        establecimientos = [dict(zip(columns, row)) for row in rows]

    return JsonResponse({
        "ruta_id": ruta_id,
        "establecimientos": establecimientos
    }, json_dumps_params={'ensure_ascii': False})