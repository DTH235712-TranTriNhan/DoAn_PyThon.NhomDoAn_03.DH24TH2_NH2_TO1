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
            # 1. TẠO VÀ KIỂM TRA USER ID TỰ ĐỘNG
            if user_id is None:
                new_user_id = str(uuid.uuid4())[:8].upper()
                
                # Lặp cho đến khi tạo được một ID duy nhất
                while checkUserIDExists(new_user_id):
                    new_user_id = str(uuid.uuid4())[:8].upper()
                
                user_id = new_user_id
            
            # 2. BỎ QUA KIỂM TRA USERNAME Ở ĐÂY VÌ ĐÃ CÓ REAL-TIME CHECK Ở GIAO DIỆN.
            #   Nếu có lỗi trùng lặp (hiếm) sẽ được bắt ở except IntegrityError.
            
            # 3. THỰC HIỆN CHÈN (Sử dụng user_id đã tạo hoặc user_id được truyền vào)
            sql = """
                INSERT INTO Users (userID, userName, password, fullName, phone, address, userRole)
                VALUES (?, ?, ?, ?, ?, ?, 'user')
            """
            cursor.execute(sql, user_id, username, password, fullname, phone, address)
            conn.commit()
            return True, f"Đăng ký thành công! Mã nhân viên của bạn là: {user_id}" 

        except pyodbc.IntegrityError as e:
            # Bắt lỗi trùng lặp Tên đăng nhập (hoặc Mã nhân viên nếu giao diện bị lỗi)
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