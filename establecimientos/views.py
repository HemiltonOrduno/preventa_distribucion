from django.shortcuts import render


def registro_cliente_view(request):
    return render(request, 'establecimientos/registro_cliente.html')


def registro_establecimiento_view(request):
    return render(request, 'establecimientos/registro_establecimiento.html')


# --- Placeholders para el API real (RF01-03), pendientes ---
class EstablecimientoListCreate:
    pass


class EstablecimientoDetail:
    pass


class RepEstablecimientoListCreate:
    pass


class RepEstablecimientoDetail:
    pass