import pyodbc
from .dbConnector import getDbConnection

def format_currency(number):
    if number is None:
        return "0"
    return "{:,.0f}".format(number).replace(",", ".")

def createOrder(userID, items_list):
    """
    Tạo đơn hàng mới, ghi vào Orders và OrderItems, đồng thời trừ tồn kho.
    """
    conn = getDbConnection()
    if not conn:
        return (False, "Lỗi kết nối CSDL.")
    
    conn.autocommit = False
    cursor = conn.cursor()
    orderID = None

    try:
        if not items_list:
            return (False, "Giỏ hàng trống. Không thể tạo đơn hàng.")

        # 1️⃣ Tính tổng tiền
        totalAmount = float(sum(item['quantity'] * item['unitPrice'] for item in items_list))

        # 2️⃣ Chèn vào bảng Orders (không dùng OUTPUT để tránh lỗi ODBC)
        cursor.execute("""
            INSERT INTO Orders (userID, totalAmount, orderDate, status)
            VALUES (?, ?, GETDATE(), ?)
        """, (userID, totalAmount, 'Completed'))
        
        # Lấy orderID mới nhất (theo người dùng)
        cursor.execute("SELECT TOP 1 orderID FROM Orders WHERE userID = ? ORDER BY orderID DESC", (userID,))
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return (False, "Không thể lấy mã đơn hàng vừa tạo.")
        
        orderID = row[0]

        # 3️⃣ Trừ tồn kho và thêm chi tiết đơn hàng
        for item in items_list:
            sku = item['sku']
            quantity = item['quantity']
            unitPrice = item['unitPrice']

            # Trừ tồn kho
            cursor.execute("""
                UPDATE Products
                SET stockQuantity = stockQuantity - ?
                WHERE SKU = ? AND stockQuantity >= ?
            """, (quantity, sku, quantity))

            if cursor.rowcount == 0:
                conn.rollback()
                return (False, f"Không đủ hàng tồn cho sản phẩm {sku}.")

            # Thêm chi tiết đơn hàng
            cursor.execute("""
                INSERT INTO OrderItems (orderID, SKU, quantity, unitPrice)
                VALUES (?, ?, ?, ?)
            """, (orderID, sku, quantity, unitPrice))

        # 4️⃣ Commit
        conn.commit()
        return (True, orderID)

    except pyodbc.IntegrityError as e:
        conn.rollback()
        msg = str(e)
        if 'FOREIGN KEY' in msg and 'Users' in msg:
            return (False, "Lỗi: userID không tồn tại. Vui lòng đăng nhập lại.")
        return (False, f"Lỗi ràng buộc: {e}")

    except Exception as e:
        conn.rollback()
        print(f"LỖI TẠO ĐƠN HÀNG KHÔNG XÁC ĐỊNH: {e}")
        return (False, f"Lỗi khi tạo đơn hàng: {e}")

    finally:
        conn.autocommit = True
        conn.close()

def getAllOrdersForAdmin():
    """Admin xem toàn bộ đơn hàng kèm người mua và sản phẩm."""
    conn = getDbConnection()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                O.orderID,
                O.orderDate,
                O.totalAmount,
                O.status,
                U.fullName,
                U.userName,
                P.name AS productName,
                OI.quantity,
                OI.unitPrice
            FROM Orders O
            JOIN Users U ON O.userID = U.userID
            JOIN OrderItems OI ON O.orderID = OI.orderID
            JOIN Products P ON OI.SKU = P.SKU
            ORDER BY O.orderDate DESC
        """)
        rows = cursor.fetchall()
        return [
            {
                "orderID": r.orderID,
                "orderDate": r.orderDate,
                "totalAmount": r.totalAmount,
                "status": r.status,
                "fullName": r.fullName,
                "userName": r.userName,
                "productName": r.productName,
                "quantity": r.quantity,
                "unitPrice": r.unitPrice,
            }
            for r in rows
        ]
    except Exception as e:
        print("Lỗi lấy đơn hàng cho admin:", e)
        return []
    finally:
        conn.close()

def getAllOrders():
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                o.orderID,
                o.orderDate,
                u.userName,
                u.fullName,
                o.totalAmount,
                o.status
            FROM Orders o
            JOIN Users u ON o.userID = u.userID
            ORDER BY o.orderDate DESC
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Lỗi lấy danh sách đơn hàng:", e)
        return []
    finally:
        conn.close()

def getOrderDetails(orderID):
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                oi.SKU,
                p.name AS productName,
                oi.quantity,
                oi.unitPrice,
                (oi.quantity * oi.unitPrice) AS totalPrice
            FROM OrderItems oi
            JOIN Products p ON oi.SKU = p.SKU
            WHERE oi.orderID = ?
        """, (orderID,))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Lỗi lấy chi tiết đơn hàng:", e)
        return []
    finally:
        conn.close()
