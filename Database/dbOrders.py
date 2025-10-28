import pyodbc
from .dbConnector import getDbConnection

# ----------------------------------------------------------------------
# --- HÀM TIỆN ÍCH ---
# ----------------------------------------------------------------------

def format_currency(number):
    """Định dạng số thành chuỗi tiền tệ Việt Nam (1.000.000)."""
    if number is None:
        return "0"
    # Thay thế dấu phẩy mặc định bằng dấu chấm theo chuẩn VN
    return "{:,.0f}".format(number).replace(",", ".")

# ----------------------------------------------------------------------
# --- LOGIC TẠO ĐƠN HÀNG VÀ TRỪ TỒN KHO (TRANSACTION) ---
# ----------------------------------------------------------------------

def createOrder(userID, items_list):
    """
    Tạo một đơn hàng mới (Orders) và các chi tiết (OrderItems), 
    đồng thời TRỪ tồn kho (Products) trong một Giao dịch (Transaction) DUY NHẤT.

    :param userID: ID người dùng tạo đơn hàng.
    :param items_list: Danh sách các dict chứa {'sku', 'quantity', 'unitPrice'}.
    :return: (True, orderID) nếu thành công, (False, error_message) nếu thất bại.
    """
    conn = getDbConnection()
    if not conn: 
        return (False, "Lỗi kết nối CSDL.")
    
    # Bắt đầu Transaction 
    conn.autocommit = False 
    cursor = conn.cursor()
    orderID = None

    try:
        if not items_list:
             return (False, "Giỏ hàng trống. Không thể tạo đơn hàng.")

        # 1. Tính tổng tiền
        raw_totalAmount = sum(item['quantity'] * item['unitPrice'] for item in items_list)
        totalAmount = float(raw_totalAmount)
        
        # 2. Chèn vào bảng Orders
        cursor.execute("""
            INSERT INTO Orders (userID, totalAmount, orderDate, status) 
            VALUES (?, ?, GETDATE(), ?)
        """, (userID, totalAmount, 'Completed'))
        
        # Lấy orderID mới được tạo
        cursor.execute("SELECT SCOPE_IDENTITY()")
        fetch_result = cursor.fetchone()
        
        if fetch_result and fetch_result[0] is not None:
            orderID = int(fetch_result[0])
        else:
            # Lỗi không lấy được ID sau khi INSERT
            conn.rollback()
            print(f"DEBUG: Lỗi INSERT Orders - SCOPE_IDENTITY trả về None.")
            return (False, "Không thể tạo mã đơn hàng mới. Lỗi chèn dữ liệu vào bảng Orders.")
        
        # 3. Chèn vào OrderItems VÀ Trừ tồn kho
        for item in items_list:
            sku = item['sku']
            quantity = item['quantity']
            unitPrice = item['unitPrice']
            
            # 3a. Trừ tồn kho: Đảm bảo tồn kho >= số lượng cần trừ
            update_query = """
                UPDATE Products 
                SET stockQuantity = stockQuantity - ? 
                WHERE SKU = ? AND stockQuantity >= ?
            """
            cursor.execute(update_query, quantity, sku, quantity)
            
            # Kiểm tra: Nếu không có dòng nào được cập nhật -> Hết hàng/SKU sai
            if cursor.rowcount == 0:
                conn.rollback() 
                return (False, f"Lỗi tồn kho hoặc SKU không hợp lệ ({sku}). Không đủ hàng để trừ.")

            # 3b. Chèn vào OrderItems
            cursor.execute("""
                INSERT INTO OrderItems (orderID, SKU, quantity, unitPrice)
                VALUES (?, ?, ?, ?)
            """, (orderID, sku, quantity, unitPrice))
            
        conn.commit() # Commit tất cả các thay đổi
        return (True, orderID)

    except pyodbc.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)
        print(f"LỖI SQL INTEGRITY: {e}") 
        
        # Bắt lỗi Khóa ngoại (Ví dụ: userID không tồn tại)
        if 'FOREIGN KEY' in error_msg and 'Users' in error_msg:
             return (False, "Lỗi: Mã người dùng (userID) không tồn tại. Vui lòng đăng nhập lại.")
        return (False, f"Lỗi ràng buộc CSDL: {e}")
        
    except Exception as e:
        conn.rollback()
        print(f"LỖI TẠO ĐƠN HÀNG KHÔNG XÁC ĐỊNH: {e}") 
        return (False, f"Lỗi hệ thống khi tạo đơn hàng: {e}")
        
    finally:
        # Quan trọng: Đặt lại autocommit và đóng kết nối
        conn.autocommit = True
        if conn:
            conn.close()