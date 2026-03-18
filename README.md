# Images CSV API

REST API generada automáticamente desde `images.csv` — Juliao Boticarios.
Construida con **FastAPI + SQLite + SQLAlchemy**. Lista para deploy en **Render.com**.

---

## Columnas del CSV

| Columna | Tipo | Nullable | Descripción |
|---|---|---|---|
| id | integer | No | Auto-generado (PK) |
| image_url | string | No | URL de la imagen |
| alt_text | string | Si | Texto alternativo |
| page_source | string | Si | Página de origen |
| width | integer | Si | Ancho en pixels |
| height | integer | Si | Alto en pixels |
| format | string | No | svg, jpg, png |
| estimated_size_kb | float | No | Tamaño estimado en KB |
| category | string | No | Categoría (misc, home, ...) |
| downloaded | boolean | No | Si fue descargada |
| local_path | string | Si | Ruta local del archivo |

---

## Endpoints

### Health
```
GET /          → Info del API
GET /docs      → Swagger UI interactivo
GET /redoc     → ReDoc
```

### Listado y detalle
```
GET /images                            → Listar todas las imágenes
GET /images/{id}                       → Obtener por ID
GET /images/columns                    → Schema de columnas
GET /images/stats                      → Estadísticas numéricas
```

### Parámetros de listado
```
?page=1&limit=50       Paginación (máx limit=500)
?sort_by=category      Ordenar por columna
?order=asc|desc        Dirección
```

### Búsqueda
```
GET /images/search
  ?q=texto                       Full-text en columnas string
  ?category=home                 Filtro exacto
  ?format=jpg                    Filtro exacto
  ?image_url_contains=nacer      LIKE parcial
  ?estimated_size_kb_gte=50      Mayor o igual (numérico)
  ?estimated_size_kb_lte=100     Menor o igual (numérico)
  ?width_gte=800
  ?downloaded=true               Filtro booleano
```

---

## Ejemplos curl

```bash
# Listar primeras 10 imágenes
curl "http://localhost:8000/images?limit=10"

# Imagen por ID
curl "http://localhost:8000/images/1"

# Buscar por categoría
curl "http://localhost:8000/images/search?category=home"

# Buscar texto en URL
curl "http://localhost:8000/images/search?image_url_contains=ama-nacer"

# Filtrar por tamaño
curl "http://localhost:8000/images/search?estimated_size_kb_gte=100"

# Ordenar por tamaño descendente
curl "http://localhost:8000/images?sort_by=estimated_size_kb&order=desc"

# Estadísticas
curl "http://localhost:8000/images/stats"
```

---

## Formato de respuesta

### Lista
```json
{
  "success": true,
  "data": [...],
  "meta": {
    "total": 341,
    "page": 1,
    "limit": 50,
    "pages": 7
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Registro con id=999 no encontrado"
  }
}
```

---

## Correr localmente

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Arrancar el servidor
uvicorn main:app --reload

# 3. Abrir en el navegador
# http://localhost:8000/docs
```

La API carga el CSV automáticamente al primer arranque. Si ya hay datos en la DB, omite la carga.

---

## Deploy en Render.com

1. **Push a GitHub:** sube el proyecto a un repositorio Git
2. **Render Dashboard → New Web Service**
3. Conectar el repositorio
4. Render detecta `render.yaml` automáticamente
5. Click **Deploy** — la API estará disponible en `https://{nombre}.onrender.com`

El disco persistente (`/opt/render/project/src/data`) guarda la DB SQLite entre deploys.

---

## Actualizar los datos

1. Reemplaza `data/images.csv` con el nuevo archivo
2. Elimina la DB en Render (Shell: `rm /opt/render/project/src/data/api_data.db`)
3. Redeploy → la API recarga el CSV automáticamente
