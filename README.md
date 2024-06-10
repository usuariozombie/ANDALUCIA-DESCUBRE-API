# API de Andalucía Descubre

La API de Andalucía Descubre está diseñada para ser fácil de usar y flexible, permitiendo a los desarrolladores acceder a la información de los lugares más emblemáticos de Andalucía, así como a la información de los eventos, platos y monumentos de la región.

## Despliegue de la API

Para desplegar la API en tu propio servidor, sigue los siguientes pasos:

1. Clona el repositorio de la API de Andalucía Descubre desde GitHub.
2. Instala las dependencias de la API utilizando el gestor de paquetes de Python PIP.
3. Configura la conexión a la base de datos MySQL en el archivo de configuración de la API.
4. Crea las tablas necesarias en la base de datos MySQL.
5. Arranca el servidor de la API utilizando el comando de Uvicorn.

### Comandos:

```bash
git clone (url del repositorio)

pip install -r requirements.txt

uvicorn main:app --reload
```

## Endpoints de la API

### /api (TOWNS)

#### /towns
- **POST**: Permite crear una nueva localidad.
- **GET**: Permite obtener la información de todas las localidades.

#### /towns/{id}
- **GET**: Permite obtener la información de una localidad en concreto.
- **PUT**: Permite actualizar la información de una localidad en concreto.
- **DELETE**: Permite eliminar una localidad en concreto.

#### /towns/{id}/events
- **GET**: Permite obtener la información de los eventos de una localidad en concreto.
- **POST**: Permite crear un nuevo evento en una localidad en concreto.
- **DELETE**: Permite eliminar un evento en una localidad en concreto.

#### /towns/{id}/dishes
- **GET**: Permite obtener la información de los platos de una localidad en concreto.
- **POST**: Permite crear un nuevo plato en una localidad en concreto.
- **DELETE**: Permite eliminar un plato en una localidad en concreto.

#### /towns/{id}/monuments
- **GET**: Permite obtener la información de los monumentos de una localidad en concreto.
- **POST**: Permite crear un nuevo monumento en una localidad en concreto.
- **DELETE**: Permite eliminar un monumento en una localidad en concreto.

### /auth (USERS)

#### /auth/register
- **POST**: Permite registrar a un nuevo usuario.

#### /auth/login
- **POST**: Permite autenticar a un usuario.

#### /auth/user-info
- **GET**: Permite obtener la información del usuario autenticado.

#### /auth/users
- **GET**: Permite obtener la información de todos los usuarios (requiere permisos de administrador).

#### /auth/admin/login
- **POST**: Permite autenticar a un administrador.

#### /auth/user/{user_id}
- **PUT**: Permite actualizar la información de un usuario en concreto (requiere permisos de administrador).
- **DELETE**: Permite eliminar a un usuario en concreto (requiere permisos de administrador).

#### /auth/logs
- **GET**: Permite obtener los registros de acciones (requiere permisos de administrador).

#### /auth/send-email
- **POST**: Permite enviar un correo electrónico.

## Securización

### JWT

La API utiliza tokens JWT (JSON Web Tokens) para proteger los endpoints y garantizar que solo los usuarios autorizados puedan acceder a la información. Los tokens JWT son cadenas de texto codificadas que contienen información sobre el usuario autenticado y una firma digital que garantiza la integridad del token.

### CORS

La API utiliza la política de CORS (Cross-Origin Resource Sharing) para permitir que los clientes web accedan a los recursos de la API desde un dominio diferente. 

Ejemplo de cabeceras CORS:

```http
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

### IP Whitelisting

La API utiliza una lista blanca de direcciones IP para restringir el acceso a los endpoints protegidos y garantizar que solo los clientes autorizados puedan acceder a la información.

## Ejemplo de Respuestas

### /towns (POST)

```json
{
    "status": 201,
    "message": "Localidad creada exitosamente",
    "data": {
        "townId": 123,
        "townName": "Nombre de la localidad",
        "townDescription": "Descripción de la localidad",
        "townImage": "url de la imagen de la localidad",
        "townMap": "url del mapa de la localidad"
    }
}
```

### /towns (GET)

```json
{
    "status": 200,
    "data": [
        {
            "townId": 123,
            "townName": "Nombre de la localidad",
            "townDescription": "Descripción de la localidad",
            "townImage": "url de la imagen de la localidad",
            "townMap": "url del mapa de la localidad"
        },
        {
            "townId": 124,
            "townName": "Otra localidad",
            "townDescription": "Descripción de otra localidad",
            "townImage": "url de la imagen de la localidad",
            "townMap": "url del mapa de la localidad"
        }
    ]
}
```

### /towns/{id} (GET)

```json
{
    "status": 200,
    "data": {
        "townId": 123,
        "townName": "Nombre de la localidad",
        "townDescription": "Descripción de la localidad",
        "townImage": "url de la imagen de la localidad",
        "townMap": "url del mapa de la localidad"
    }
}
```

### /auth/register (POST)

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### /auth/login (POST)

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### /auth/user-info (GET)

```json
{
    "user_info": "usuario@example.com"
}
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue los pasos a continuación para contribuir al proyecto:

1. Realiza un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios necesarios y realiza commits (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`).
5. Crea un nuevo Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Para más detalles, consulta el archivo LICENSE en este repositorio.

Para más información visita [Documentación de Andalucía Descubre](https://usuariozombie.github.io/ANDALUCIA-DESCUBRE-DOCS)
