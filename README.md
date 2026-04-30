# Sistema de Gestion de Encomiendas

Proyecto base en Django para la sesion 02. Incluye las apps `envios`, `clientes` y `rutas`, configuracion por variables de entorno, Docker y PostgreSQL.

## Ejecutar con Docker

```bash
docker compose up --build -d
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Accesos

- App: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`
- pgAdmin: `http://localhost:5050`

## pgAdmin

Credenciales web por defecto:

- Usuario: `admin@encomiendas.com`
- Password: `admin123`

El servicio PostgreSQL del proyecto queda preconfigurado en pgAdmin con:

- Host: `db`
- Puerto: `5432`
- Base de datos: `encomiendas_db`
- Usuario BD: `encomiendas_user`

Si cambias `DB_NAME` o `DB_USER`, actualiza tambien `docker/pgadmin/servers.json` o registra el servidor manualmente desde la interfaz web.
