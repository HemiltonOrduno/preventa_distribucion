from django.shortcuts import render


def ruta_del_dia_view(request):
    return render(request, 'visitas/ruta_del_dia.html')


def visita_view(request):
    return render(request, 'visitas/visita.html')


def levantar_pedido_view(request):
    return render(request, 'visitas/levantar_pedido.html')


def visita_sin_pedido_view(request):
    return render(request, 'visitas/visita_sin_pedido.html')


# --- Placeholders para el API real (RF04-15), pendientes ---
class VisitaListCreate:
    pass


class VisitaDetail:
    pass


class PedidoListCreate:
    pass


class PedidoDetail:
    pass


class AjustarDetallePedido:
    pass