import oracledb

DB_USER = "carbon_user"
DB_PASSWORD = "Carbon123"
DB_DSN = "localhost:1521/XEPDB1"

def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )

