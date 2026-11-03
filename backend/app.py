from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from routes.auth_routes import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

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

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
