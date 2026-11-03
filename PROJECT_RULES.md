# Reglas del repositorio

1. `frontend/` no contiene credenciales ni SQL.
2. `backend/` es la única capa que accede a SQL Server.
3. `database/` contiene scripts SQL versionados y numerados.
4. `docs/` describe decisiones de arquitectura y contratos de API.
5. No subir `node_modules`, `.venv`, `.env`, builds ni credenciales.
6. Antes de agregar una dependencia, comprobar que sea necesaria.
