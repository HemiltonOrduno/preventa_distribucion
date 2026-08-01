from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
from django.shortcuts import render  # agrégalo al import existente
from usuarios.permissions import rol_requerido

TIPOS_SALIDA = ('TM002', 'TM003')  # Salida por pedido, Salida por merma

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def registrar_movimiento(request):
    """
    RF40 (entrada) y RF42 (salida por merma): registra un movimiento de
    inventario con sus líneas de detalle.

    El stock de cada producto se actualiza solo (RF43) porque ya existe
    el trigger tg_actualizar_stock, que dispara AFTER INSERT ON
    detalle_movimiento. Por eso aquí NUNCA tocamos producto.stock a mano
    — si lo hiciéramos, se sumaría/restaría dos veces.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        tipo_movimiento = body.get("tipo_movimiento")
        observaciones = body.get("observaciones", "")
        empleado = body.get("empleado")
        detalle = body.get("detalle", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not tipo_movimiento or not empleado or not detalle:
        return JsonResponse({"error": "Se requiere tipo_movimiento, empleado y detalle"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            # El trigger solo resta stock, no valida que no quede negativo.
            # Por eso lo checamos aquí ANTES de insertar cualquier cosa.
            if tipo_movimiento in TIPOS_SALIDA:
                for linea in detalle:
                    cursor.execute("SELECT stock FROM producto WHERE codigo = %s", [linea["producto"]])
                    row = cursor.fetchone()
                    if not row:
                        return JsonResponse({"error": f"Producto {linea['producto']} no encontrado"}, status=404)
                    if linea["cantidad"] > row[0]:
                        return JsonResponse({
                            "error": f"Stock insuficiente para {linea['producto']}. Disponible: {row[0]}"
                        }, status=400)

            # codigo no es autoincremental en el esquema real (igual que
            # pasó con usuario.num) -> lo calculamos nosotros.
            cursor.execute("SELECT COALESCE(MAX(codigo), 0) + 1 FROM movimientos")
            nuevo_codigo = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO movimientos (codigo, observaciones, fecha, tipo_movimiento, empleado)
                VALUES (%s, %s, NOW(), %s, %s)
            """, [nuevo_codigo, observaciones, tipo_movimiento, empleado])

            for linea in detalle:
                subtotal = linea["cantidad"] * linea["precio_unitario"]
                cursor.execute("""
                    INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, [nuevo_codigo, linea["producto"], linea["cantidad"], linea["precio_unitario"], subtotal])
                # ↑ Este INSERT es el que dispara tg_actualizar_stock.

    return JsonResponse({
        "mensaje": "Movimiento registrado correctamente",
        "movimiento_id": nuevo_codigo,
        "tipo_movimiento": tipo_movimiento,
        "productos_afectados": len(detalle)
    }, status=201, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def consultar_stock(request, cod_producto):
    """
    RF18: consulta el stock disponible de un producto específico.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT codigo, nombre, stock FROM producto WHERE codigo = %s", [cod_producto])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)

    return JsonResponse({
        "producto": row[0], "nombre": row[1], "stock": row[2]
    }, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def almacenista_movimientos_view(request):
    return render(request, 'inventario/movimientos.html')