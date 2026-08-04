from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from usuarios.permissions import rol_requerido


@rol_requerido('Administrador')
def pedidos_activos_view(request):
    return render(request, 'reportes/pedidos_activos.html')


@rol_requerido('Administrador')
def pedidos_activos_api(request):
    """
    RF49: estado actual de todos los pedidos activos.
    "Activos" = cualquier pedido que no esté Cancelado ni ya Entregado
    (cubre todo el ciclo intermedio: pendiente de validación, en proceso,
    registrado, surtido).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.num AS pedido_id,
                p.fecha,
                p.total,
                ep.nombre AS estado,
                e.nombre AS establecimiento_nombre,
                z.nombre AS zona_nombre,
                CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor
            FROM pedido p
            INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN zona z ON z.num = e.zona
            INNER JOIN empleado em ON em.num = v.empleado
            WHERE ep.nombre NOT IN ('Cancelado', 'Entregado')
            ORDER BY p.fecha DESC
        """)
        columns = [col[0] for col in cursor.description]
        pedidos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in pedidos:
        p['total'] = float(p['total'])

    return JsonResponse({
        "pedidos": pedidos,
        "total_activos": len(pedidos)
    }, json_dumps_params={'ensure_ascii': False})