# Arquitectura de Manos Amigas

## Flujo principal

```text
React + Vite (frontend)
        |
        | HTTP / JSON
        v
Flask REST API (backend)
        |
        | pyodbc
        v
SQL Server (base de datos)
        |
        v
SSMS 22 (administración)
```

## Reglas de arquitectura

1. El frontend nunca se conecta directamente a SQL Server.
2. Las credenciales de la base de datos permanecen exclusivamente en el backend.
3. El frontend consume únicamente endpoints bajo `/api`.
4. Las consultas SQL deben ser parametrizadas.
5. Las contraseñas nunca se guardan en texto plano.
6. `routes/` recibe y responde HTTP; la lógica de negocio debe ir en `services/`.
7. Los scripts SQL se ejecutan en orden numérico.
8. Cada funcionalidad importante debe incorporar una prueba cuando sea implementada.
