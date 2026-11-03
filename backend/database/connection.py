import pyodbc
from config import Config


def get_connection():
    trust_cert = "yes" if Config.DB_TRUST_SERVER_CERTIFICATE else "no"

    if Config.DB_TRUSTED_CONNECTION:
        connection_string = (
            f"DRIVER={{{Config.DB_DRIVER}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            "Trusted_Connection=yes;"
            f"TrustServerCertificate={trust_cert};"
        )
    else:
        connection_string = (
            f"DRIVER={{{Config.DB_DRIVER}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"TrustServerCertificate={trust_cert};"
        )

    return pyodbc.connect(connection_string)
