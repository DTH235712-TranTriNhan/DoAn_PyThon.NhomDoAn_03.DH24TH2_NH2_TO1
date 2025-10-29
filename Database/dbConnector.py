import pyodbc

# ----------------------------------------------------------------------
# --- CẤU HÌNH KẾT NỐI CSDL ---
# ----------------------------------------------------------------------
SERVER_NAME = r'LAPTOP-T018HFGU'
DATABASE_NAME = 'salesProjectDB'
DRIVER = '{ODBC Driver 17 for SQL Server}'
# ----------------------------------------------------------------------

def getDbConnection(user=None, password=None):
    """
    Tạo và trả về đối tượng kết nối CSDL SQL Server.
    Mặc định sử dụng Windows Authentication nếu không có user/password.
    """
    try:
        if user and password:
            # Chế độ SQL Server Authentication
            conn_string = (
                f'DRIVER={DRIVER};'
                f'SERVER={SERVER_NAME};'
                f'DATABASE={DATABASE_NAME};'
                f'UID={user};'
                f'PWD={password};'
            )
        else:
            # Chế độ Windows Authentication
            conn_string = (
                f'DRIVER={DRIVER};'
                f'SERVER={SERVER_NAME};'
                f'DATABASE={DATABASE_NAME};'
                'Trusted_Connection=yes;'
            )
        
        # Thiết lập kết nối
        conn = pyodbc.connect(conn_string)
        # Thiết lập autocommit mặc định là True cho các thao tác đơn giản
        conn.autocommit = True 
        
        return conn
        
    except Exception as e:
        print(f"Lỗi kết nối CSDL SQL Server: {e}")
        return None