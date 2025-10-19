from .dbConnector import getDbConnection
import uuid # Dùng để tạo ID duy nhất tạm thời nếu bạn không muốn tự nhập
import pyodbc

def checkLogin(username, password):
    """Kiểm tra tên đăng nhập và mật khẩu, trả về vai trò nếu hợp lệ."""
    conn = getDbConnection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT userRole FROM Users WHERE userName = ? AND password = ?"
        
        try:
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0] 
            return None 
        except Exception as e:
            print(f"Lỗi kiểm tra đăng nhập: {e}")
            conn.close()
            return None
    return None

def registerUser(user_id, username, password, fullname, phone, address):
    conn = getDbConnection()
    if conn:
        cursor = conn.cursor()
        try:
            # *** PHẦN NÀY ĐÃ ĐƯỢC DỌN DẸP ***
            # Loại bỏ SELECT kiểm tra trùng lặp vì đã kiểm tra ở giao diện
            
            sql = """
                INSERT INTO Users (userID, userName, password, fullName, phone, address, userRole)
                VALUES (?, ?, ?, ?, ?, ?, 'user')
            """
            cursor.execute(sql, user_id, username, password, fullname, phone, address)
            conn.commit()
            return True, "Đăng ký tài khoản thành công! Vui lòng đăng nhập."

        except pyodbc.IntegrityError as e:
            # Bắt lỗi cuối cùng: Nếu có lỗi trùng lặp xảy ra giữa lúc gõ phím và lúc nhấn nút
            # (Rất hiếm, nhưng đảm bảo an toàn CSDL)
            error_msg = str(e)
            if 'PRIMARY KEY' in error_msg or 'userID' in error_msg:
                return False, "Lỗi: Mã Nhân viên đã bị tài khoản khác sử dụng ngay lập tức."
            elif 'UNIQUE' in error_msg or 'userName' in error_msg:
                return False, "Lỗi: Tên đăng nhập đã bị tài khoản khác sử dụng ngay lập tức."
            return False, f"Lỗi ràng buộc CSDL: {e}"
            
        except Exception as e:
            return False, f"Lỗi không xác định khi đăng ký: {e}"
            
        finally:
            if conn:
                conn.close()
    return False, "Không thể kết nối đến CSDL."

def checkUserIDExists(user_id):
    conn = getDbConnection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT userID FROM Users WHERE userID = ?", user_id)
            return cursor.fetchone() is not None # Trả về True nếu tìm thấy
        except Exception:
            return False
        finally:
            conn.close()
    return False

def checkUserNameExists(username):
    conn = getDbConnection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT userName FROM Users WHERE userName = ?", username)
            return cursor.fetchone() is not None # Trả về True nếu tìm thấy
        except Exception:
            return False
        finally:
            conn.close()
    return False