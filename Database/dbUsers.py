from .dbConnector import getDbConnection
import uuid 
import pyodbc

# ----------------------------------------------------------------------
# --- HÀM KIỂM TRA ĐĂNG NHẬP ---
# ----------------------------------------------------------------------

def checkLogin(username, password):
    """Kiểm tra tên đăng nhập và mật khẩu, trả về userID và vai trò nếu hợp lệ."""
    conn = getDbConnection()
    if not conn: 
        return None, None
        
    cursor = conn.cursor()
    query = "SELECT userID, userRole FROM Users WHERE userName = ? AND password = ?"
    
    try:
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            user_role = result[1]
            return user_id, user_role 
            
        return None, None
            
    except Exception as e:
        print(f"Lỗi kiểm tra đăng nhập: {e}")
        return None, None
            
    finally:
        if conn:
            conn.close()

# ----------------------------------------------------------------------
# --- HÀM ĐĂNG KÝ NGƯỜI DÙNG ---
# ----------------------------------------------------------------------

def registerUser(user_id, username, password, fullname, phone, address):
    """
    Đăng ký người dùng mới.
    - Tự động sinh userID nếu user_id là None.
    - Mặc định userRole = 'User' (viết hoa đúng ràng buộc CHECK).
    """
    conn = getDbConnection()
    if not conn:
        return False, "Không thể kết nối đến CSDL."

    cursor = conn.cursor()

    try:
        # 1️ Tạo userID ngẫu nhiên nếu chưa có
        if user_id is None:
            # Dạng: US + 6 ký tự đầu UUID (VD: US3A92F)
            new_user_id = "US" + str(uuid.uuid4()).replace("-", "")[:6].upper()
            while checkUserIDExists(new_user_id):
                new_user_id = "US" + str(uuid.uuid4()).replace("-", "")[:6].upper()
            user_id = new_user_id

        # 2️ Chèn dữ liệu vào bảng Users
        sql = """
            INSERT INTO Users (userID, userName, password, fullName, phone, address, userRole)
            VALUES (?, ?, ?, ?, ?, ?, 'User')
        """
        cursor.execute(sql, (user_id, username, password, fullname, phone, address))
        conn.commit()
        return True, f"Đăng ký thành công! Mã người dùng của bạn là {user_id}"

    except pyodbc.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)

        # Bắt lỗi khóa chính hoặc tên đăng nhập trùng
        if "PRIMARY KEY" in error_msg or "userID" in error_msg:
            return False, "Lỗi: Mã người dùng đã tồn tại."
        elif "UNIQUE" in error_msg or "userName" in error_msg:
            return False, "Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác."
        return False, f"Lỗi ràng buộc CSDL: {e}"

    except Exception as e:
        conn.rollback()
        return False, f"Lỗi không xác định khi đăng ký: {e}"

    finally:
        if conn:
            conn.close()

# ----------------------------------------------------------------------
# --- HÀM KIỂM TRA TỒN TẠI ---
# ----------------------------------------------------------------------

def checkUserIDExists(user_id):
    """Kiểm tra user ID đã tồn tại trong CSDL hay chưa."""
    conn = getDbConnection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT userID FROM Users WHERE userID = ?", (user_id,))
        return cursor.fetchone() is not None
    except Exception:
        return False
    finally:
        conn.close()


def checkUserNameExists(username):
    """Kiểm tra tên đăng nhập đã tồn tại trong CSDL hay chưa."""
    conn = getDbConnection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT userName FROM Users WHERE userName = ?", (username,))
        return cursor.fetchone() is not None
    except Exception:
        return False
    finally:
        conn.close()