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
