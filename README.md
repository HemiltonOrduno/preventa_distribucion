# Sistema Web de Preventa y Distribución

Sistema web desarrollado para digitalizar y centralizar el ciclo completo de preventa y distribución de productos. Conecta en tiempo real a vendedores, almacenistas, coordinadores y repartidores, permitiendo el levantamiento de pedidos en campo, validación de inventario, planificación de rutas y confirmación de entregas desde una sola plataforma.


## Equipo de desarrollo
- Contreras Rangel Samanta Denisse
- Fonseca De La Cruz Jesus Gildardo
- Morales Aparicio Irving De Jesus
- Orduño Santiago Hemilton Raul



## Tecnologías
- Python / Django / Django REST Framework
- MySQL
- HTML5 / CSS3
- OSRM (optimización de rutas)



## Instalación

1. Clonar el repositorio
2. Crear y activar el entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```
3. Instalar dependencias
```bash
pip install -r requirements.txt
```
4. Configurar el archivo .env con las variables de entorno
5. Crear la base de datos en MySQL
6. Ejecutar migraciones
```bash
python manage.py migrate
```
7. Iniciar el servidor
```bash
python manage.py runserver
```

## Estructura del proyecto
```
preventa_distribucion/
├── config/          # Configuración del proyecto
├── usuarios/        # Gestión de usuarios y roles
├── establecimientos/ # Gestión de clientes y establecimientos
├── visitas/         # Visitas y pedidos
├── productos/       # Catálogo de productos
├── inventario/      # Movimientos de inventario
├── rutas/           # Planificación de rutas
├── entregas/        # Distribución y entregas
├── reportes/        # Reportes administrativos
├── database/        # Scripts SQL
├── static/          # Archivos estáticos
├── media/           # Archivos subidos
└── templates/       # Plantillas HTML
```