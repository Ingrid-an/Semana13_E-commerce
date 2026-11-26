# API REST — TecnoMarket Perú (E-commerce de Tecnología)

**Asignatura:** Desarrollo de Aplicaciones Web (IS093A) · Unidad II — Desarrollo Web Fullstack
**Práctica:** Semana 13 — Grupal · **Caso 2 de 2**
**Tema:** Django REST Framework — Serialización avanzada, ViewSets, Routers, filtrado, paginación, throttling, autenticación por token y documentación OpenAPI.

API REST para una tienda en línea de productos tecnológicos construida con
**Django + Django REST Framework**, consumida por una interfaz web minimalista
en JavaScript puro (fetch).

---

## Integrantes y roles

| Rol | Responsabilidad |
|---|---|
| Arquitecto de API | startproject/startapp, settings DRF, routers, estructura |
| Ingeniero de Serializers | ModelSerializer, HyperlinkedModelSerializer, nested, validaciones |
| Desarrollador de ViewSets | ModelViewSet, @action, permisos, filtros, throttling |
| QA & Documentación | pruebas con curl, poblado de datos, Swagger, README |

> Trabajo desarrollado de forma individual (práctica nominalmente grupal).

---

## Arquitectura del proyecto

```
caso2_ecommerce/
├── manage.py
├── requirements.txt
├── .gitignore                 excluye db.sqlite3 y __pycache__
├── config/                    proyecto Django
│   ├── settings.py            INSTALLED_APPS, REST_FRAMEWORK, CORS, SPECTACULAR
│   └── urls.py                / (interfaz) + /api/ (router) + swagger + redoc
└── tienda/                    la app
    ├── models.py              Categoria, Producto, Resena, Orden, ItemOrden
    ├── serializers.py         serialización avanzada (nested + HATEOAS + validaciones)
    ├── views.py               ViewSets + @action + filtros + throttling
    ├── urls.py                DefaultRouter (productos / resenas / ordenes)
    ├── admin.py               registro en el panel de administración
    ├── templates/index.html   interfaz web (fetch a /api/productos/)
    └── management/commands/
        └── populate_data.py   datos de ejemplo (100 productos, etc.)
```

---

## Modelo de datos

| Modelo | Campos clave | Propiedades calculadas |
|---|---|---|
| **Categoria** | nombre, descripcion, imagen | — |
| **Producto** | sku, nombre, marca, categoria (FK), precio, descuento, stock, especificaciones (JSON) | `precio_con_descuento`, `disponible`, `rating_promedio` |
| **Resena** | producto (FK), usuario (FK), calificacion, titulo, comentario | `es_compra_verificada` |
| **Orden** | usuario (FK), direccion_envio, metodo_pago, estado, total, numero_seguimiento | `tiempo_estimado_entrega` (+4 días) |
| **ItemOrden** | orden (FK), producto (FK), cantidad, precio_compra (snapshot) | — |

Índices en `marca` y `categoria` de Producto para optimizar las búsquedas.

---

## Requerimientos funcionales cubiertos

- **RF1 — Serialización avanzada de Producto:** `ProductoSerializer` (HyperlinkedModelSerializer)
  con **categoría anidada** (nested, solo lectura) + `categoria_id` (solo escritura),
  **3 campos calculados** (`precio_con_descuento`, `rating_promedio`, `disponible`),
  campo `url` (**HATEOAS**) y validación de precio.
- **RF2 — Filtrado, búsqueda y ordenamiento:** rango de precio
  (`precio_min` / `precio_max` con `NumberFilter`), filtro por `categoria` y `marca`
  (`DjangoFilterBackend`), búsqueda full-text (`SearchFilter` en nombre/descripción/marca)
  y ordenamiento (`OrderingFilter` por precio/fecha).
- **RF3 — Órdenes con items anidados:** `OrdenSerializer` con `items` anidados
  (snapshot del precio de compra), campo calculado `tiempo_estimado_entrega`,
  y `@action cancelar` + `@action mis_ordenes`.
- **RF4 — Reseñas con validación:** `ResenaSerializer` con validación de calificación
  (1–5), campo calculado `es_compra_verificada`, y asignación automática del usuario
  autenticado al crear.
- **RF5 — Seguridad:** autenticación por **Token** + **Session**, permisos
  (`IsAuthenticatedOrReadOnly`), *throttling* por alcance (`search`, `checkout`),
  CORS y documentación OpenAPI (Swagger / ReDoc).

---

## Serialización — técnicas aplicadas

| Técnica | Dónde |
|---|---|
| `ModelSerializer` | CategoriaSerializer, ItemOrdenSerializer |
| `HyperlinkedModelSerializer` (HATEOAS) | ProductoSerializer, ResenaSerializer, OrdenSerializer |
| Serialización **anidada** (nested) | categoría dentro de producto; items dentro de orden |
| `SerializerMethodField` | `disponible` |
| `ReadOnlyField` | `precio_con_descuento`, `rating_promedio`, `es_compra_verificada`, `tiempo_estimado_entrega` |
| `PrimaryKeyRelatedField` | `categoria_id` (write), `producto`, `usuario` |
| `validate_<campo>()` | `validate_precio`, `validate_calificacion` |
| `read_only_fields` | total, numero_seguimiento, usuario (asignados por el servidor) |

---

## Endpoints

Base: `http://localhost:8000/api/`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/api/productos/` | Lista paginada (24/pág) | Pública |
| GET | `/api/productos/{id}/` | Detalle de producto | Pública |
| GET | `/api/productos/?precio_min=&precio_max=` | Filtro por rango de precio | Pública |
| GET | `/api/productos/?categoria=&marca=` | Filtro por categoría / marca | Pública |
| GET | `/api/productos/?search=` | Búsqueda (nombre/desc/marca) | Pública |
| GET | `/api/productos/?ordering=precio` | Ordenamiento | Pública |
| GET | `/api/productos/{id}/resenas/` | **@action**: reseñas del producto | Pública |
| GET/POST | `/api/resenas/` | Listar / crear reseña (usuario automático) | POST requiere login |
| GET | `/api/ordenes/` | Órdenes **del usuario autenticado** | Requiere login |
| POST | `/api/ordenes/{id}/cancelar/` | **@action**: cancelar (solo pendientes) | Requiere login |
| GET | `/api/ordenes/mis_ordenes/` | **@action**: mis órdenes | Requiere login |

**Documentación interactiva:**
- Swagger UI → `http://localhost:8000/api/docs/`
- ReDoc → `http://localhost:8000/api/redoc/`
- Esquema OpenAPI → `http://localhost:8000/api/schema/`

---

## Autenticación por Token

```bash
# 1. Obtener un token (usuario de ejemplo)
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=cliente1&password=tecno2026"

# 2. Usar el token en las peticiones protegidas
curl http://localhost:8000/api/ordenes/ \
  -H "Authorization: Token <tu_token>"
```

---

## Cómo ejecutar (paso a paso)

Requiere **Python 3.11+** y conexión a internet (Swagger carga su UI desde un CDN).

```bash
# 1. (opcional) entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac

# 2. instalar dependencias
pip install -r requirements.txt

# 3. migraciones
python manage.py makemigrations
python manage.py migrate

# 4. poblar datos de ejemplo
python manage.py populate_data

# 5. (opcional) superusuario para el admin
python manage.py createsuperuser

# 6. arrancar el servidor
python manage.py runserver
```

Abrir:
- **Interfaz web:** http://localhost:8000/
- **API navegable:** http://localhost:8000/api/productos/
- **Swagger:** http://localhost:8000/api/docs/
- **Admin:** http://localhost:8000/admin/

### Usuarios de prueba (creados por `populate_data`)
- `cliente1` … `cliente20` — contraseña: **tecno2026**

---

## Datos de ejemplo poblados

- 6 categorías · 100 productos · 20 usuarios · 50 órdenes · 100 reseñas.
- Los IDs se reinician en cada ejecución de `populate_data` (resultados reproducibles).

---

## Configuración DRF (settings.py)

- **Paginación:** `PageNumberPagination`, 24 por página.
- **Autenticación:** `TokenAuthentication` + `SessionAuthentication`.
- **Throttling:** anónimo `60/hour`, usuario `2000/hour`,
  `search 100/hour`, `checkout 10/hour`.
- **CORS:** habilitado para el frontend (`django-cors-headers`).
- **OpenAPI:** `drf-spectacular` (Swagger + ReDoc).

---

## Notas de la rúbrica

- `db.sqlite3`, `__pycache__/` y `.env` en `.gitignore` (no se suben al repositorio).
- `python manage.py check` sin problemas; servidor sin errores 500.
- La interfaz consume **datos reales** de la API vía `fetch()`.
- Diseño minimalista con acentos de color, distinto del Caso 1 (Biblioteca).
