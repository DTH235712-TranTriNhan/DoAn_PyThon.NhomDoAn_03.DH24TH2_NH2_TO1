import pyodbc

SERVER_NAME = r'LAPTOP-LOMSLJ90\SQLEXPRESS'
DATABASE_NAME = 'salesProjectDB'
DRIVER = '{ODBC Driver 17 for SQL Server}'

def getDbConnection(user=None, password=None):
    """
    Tạo và trả về đối tượng kết nối CSDL SQL Server.
    
    Sử dụng Windows Authentication nếu user và password là None.
    Sử dụng SQL Server Authentication nếu user và password được cung cấp.
    """
    try:
        if user and password:
            # Chế độ SQL Server Authentication (Dùng trên máy người khác)
            conn_string = (
                f'DRIVER={DRIVER};'
                f'SERVER={SERVER_NAME};'
                f'DATABASE={DATABASE_NAME};'
                f'UID={user};'
                f'PWD={password};'
            )
        else:
            # Chế độ Windows Authentication (Dùng trên máy của bạn)
            conn_string = (
                f'DRIVER={DRIVER};'
                f'SERVER={SERVER_NAME};'
                f'DATABASE={DATABASE_NAME};'
                'Trusted_Connection=yes;'  # Xác thực bằng tài khoản Windows
            )
        
        conn = pyodbc.connect(conn_string)
        return conn
        
    except Exception as e:
        # Trong trường hợp kết nối thất bại, in ra lỗi
        print(f"Lỗi kết nối CSDL SQL Server: {e}")
        return None

# Ví dụ về cách sử dụng hàm này:

# 1. Kết nối trên máy bạn (Windows Auth)
# conn_local = get_db_connection()

# 2. Kết nối trên máy khác (SQL Server Auth)
# conn_remote = get_db_connection(user="sa", password="matkhaucuaban")

def checkLogin(username, password):
    """Kiểm tra tên đăng nhập và mật khẩu, trả về vai trò nếu hợp lệ."""
    conn = getDbConnection() # Thử kết nối bằng Windows Auth trước
    if conn:
        cursor = conn.cursor()
        # Lưu ý: Trong SQL Server, tên bảng và cột phân biệt chữ hoa/thường tùy cài đặt, nên dùng tên chính xác.
        query = "SELECT userRole FROM Users WHERE userName = ? AND password = ?"
        
        # Thực thi truy vấn với tham số để ngăn SQL Injection
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]  # Trả về role ('admin', 'user', 'guest')
        return None 
    return None
