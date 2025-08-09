# PrintShop - Gestión de Órdenes

Aplicación web modular para gestionar órdenes de una imprenta.

## Requisitos
- Docker y Docker Compose

## Arranque

1. Copiar variables de entorno:

```bash
cp .env.example .env
```

2. Levantar servicios:

```bash
docker compose up --build
```

3. Acceder a la app: http://localhost:8000
   - MailHog (correo de prueba): http://localhost:8025

Se crea automáticamente un usuario admin si la tabla `usuarios` está vacía.

Credenciales por defecto:
- Email: `admin@printshop.local`
- Password: `admin1234`

## Estructura
- `app/` aplicación Flask con factory pattern y blueprints
- `app/models.py` modelos principales
- `app/modules/*` módulos (clientes, vendedores, órdenes, pagos, usuarios, configuraciones, dashboard, calendario)
- `entrypoint.sh` inicializa migraciones y arranca el servidor

## Migraciones
Las migraciones se ejecutan automáticamente al iniciar el contenedor. Para generar nuevas manualmente:

```bash
docker compose exec web flask db migrate -m "cambio"
docker compose exec web flask db upgrade
```