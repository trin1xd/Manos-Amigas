import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from config import Config
from routes.auth_routes import auth_bp
from routes.operations_routes import ops_bp
from routes.verificacion_routes import verificacion_bp
from routes.seguimiento_routes import seguimiento_bp
from routes.notificaciones_routes import notificaciones_bp
from routes.disponibilidad_routes import disponibilidad_bp
from routes.agenda_routes import agenda_bp
from routes.verificacion_institucional_routes import institucional_bp
from routes.calificaciones_routes import calificaciones_bp
from routes.chat_routes import chat_bp
from routes.recuperacion_routes import recuperacion_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def custom_unauthorized_response(error_string):
        return jsonify({
            "success": False,
            "message": "Token de autenticación no proporcionado.",
        }), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(error_string):
        return jsonify({
            "success": False,
            "message": "Token de autenticación inválido.",
        }), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "El token de autenticación ha expirado.",
        }), 401

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ops_bp, url_prefix='/api')
    app.register_blueprint(verificacion_bp, url_prefix='/api/admin')
    app.register_blueprint(seguimiento_bp, url_prefix='/api')
    app.register_blueprint(notificaciones_bp, url_prefix='/api')
    app.register_blueprint(disponibilidad_bp, url_prefix='/api')
    app.register_blueprint(agenda_bp, url_prefix='/api')
    app.register_blueprint(institucional_bp, url_prefix='/api')
    app.register_blueprint(calificaciones_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(recuperacion_bp, url_prefix='/api')

    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):  # 404, 405, etc. conservan su código
            return jsonify({"success": False, "message": error.description}), error.code
        # Errores de código o de conexión a SQL Server: respuesta JSON sin detalles internos.
        app.logger.exception("Error inesperado: %s", error)
        return jsonify({"success": False, "message": "Error interno del servidor."}), 500

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "manos-amigas-api"})

    # Diagnóstico temporal SOLO para el backend de prueba. No revela datos,
    # contraseñas ni detalles de errores de conexión.
    if os.getenv("ENABLE_DB_DIAGNOSTIC", "false").lower() == "true":
        @app.get("/api/health/database")
        def database_health():
            from database.backend import engine
            from database.connection import get_connection

            if engine() != "postgres":
                return jsonify({"status": "unavailable"}), 503
            try:
                conn = get_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT 1 FROM public."Roles" LIMIT 1')
                        role_exists = cursor.fetchone() is not None
                        cursor.execute('SELECT 1 FROM public."Servicios" LIMIT 1')
                        service_exists = cursor.fetchone() is not None
                finally:
                    conn.close()
                if not (role_exists and service_exists):
                    return jsonify({"status": "unavailable"}), 503
                return jsonify({"status": "ok", "database": "postgres"}), 200
            except Exception:
                app.logger.exception("Fallo del diagnóstico privado de base de datos")
                return jsonify({"status": "unavailable"}), 503

    return app


if __name__ == "__main__":
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    puerto = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    if debug and host not in ('127.0.0.1', 'localhost', '::1'):
        raise SystemExit('No se permite FLASK_DEBUG=true fuera de localhost.')
    # Servidor de desarrollo. Para producción usar WSGI y HTTPS, nunca app.py.
    create_app().run(host=host, port=puerto, debug=debug)
