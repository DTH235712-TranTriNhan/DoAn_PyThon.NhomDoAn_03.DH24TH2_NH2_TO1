# File: Database/db_products.py
from .dbConnector import getDbConnection

def getAllProducts():
    """Lấy tất cả sản phẩm có tồn kho > 0 và sử dụng SKU làm ID."""
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        # THAY ĐỔI: Chọn SKU thay vì productID và lọc stockQuantity > 0
        cursor.execute("SELECT SKU, name, category, price, stockQuantity FROM Products WHERE stockQuantity > 0")
        rows = cursor.fetchall()
        
        for row in rows:
            sku = row[0]
            name = row[1]
            category = row[2]
            price = row[3]
            stock = int(row[4])
            
            # Format giá
            try:
                price_str = f"{float(price):,.0f}"
            except:
                price_str = str(price)
            
            formatted_product = (
                sku, 
                name.strip("'") if isinstance(name, str) else name,
                category.strip("'") if isinstance(category, str) else category,
                price_str,
                stock
            )
            products.append(formatted_product)
            
    except Exception as e:
        print(f"Lỗi khi tải sản phẩm: {e}")
    finally:
        if conn:
            conn.close()
        
    return products

def addProduct(sku, name, category, price, stock):
    """Thêm/Cập nhật sản phẩm. Nếu tên đã có, cộng dồn số lượng. Yêu cầu cung cấp SKU."""
    conn = getDbConnection()
    if not conn: return False, "Không thể kết nối CSDL."
        
    cursor = conn.cursor()
    name = name.strip()
    sku = sku.strip()
    
    if not sku: return False, "Mã SP (SKU) không được để trống."
    
    try:
        # 1. KIỂM TRA TRÙNG TÊN SẢN PHẨM (Ưu tiên: Cộng dồn)
        cursor.execute("SELECT SKU, stockQuantity FROM Products WHERE name = ?", name)
        existing_by_name = cursor.fetchone()

        if existing_by_name:
            # Tên đã tồn tại: CẬP NHẬT TỒN KHO VÀ THÔNG TIN (Dùng SKU cũ)
            product_sku_old = existing_by_name[0]
            current_stock = existing_by_name[1]
            new_stock = current_stock + stock
            
            sql_update = """
                UPDATE Products 
                SET category = ?, price = ?, stockQuantity = ? 
                WHERE SKU = ? 
            """
            cursor.execute(sql_update, category, price, new_stock, product_sku_old)
            message = f"Sản phẩm '{name}' (SKU: {product_sku_old}) đã có. Đã cộng dồn {stock} đơn vị. Tồn kho mới: {new_stock}."
            
        else:
            # Tên mới: Phải kiểm tra SKU đã tồn tại chưa
            cursor.execute("SELECT SKU FROM Products WHERE SKU = ?", sku)
            if cursor.fetchone():
                return False, f"Lỗi: Mã sản phẩm (SKU) '{sku}' đã được sử dụng. Vui lòng chọn Mã khác."

            # Tên mới VÀ SKU mới: CHÈN
            sql_insert = """
                INSERT INTO Products (SKU, name, category, price, stockQuantity)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql_insert, sku, name, category, price, stock)
            message = f"Đã thêm sản phẩm mới (SKU: {sku})."

        conn.commit()
        return True, message
        
    except Exception as e:
        print(f"Lỗi khi thêm/cập nhật sản phẩm: {e}")
        return False, f"Lỗi CSDL: {e}"
        
    finally:
        conn.close()

def updateProduct(sku, name, category, price, stock):
    """Cập nhật thông tin sản phẩm dựa trên SKU."""
    conn = getDbConnection()
    if conn:
        try:
            cursor = conn.cursor()
            # Kiểm tra trùng tên (Trừ chính SKU đang sửa)
            cursor.execute("SELECT SKU FROM Products WHERE name = ? AND SKU != ?", name, sku)
            if cursor.fetchone():
                return False, f"Lỗi: Tên sản phẩm '{name}' đã được sử dụng bởi SKU khác."

            query = """
            UPDATE Products SET name = ?, category = ?, price = ?, stockQuantity = ? 
            WHERE SKU = ?
            """
            cursor.execute(query, (name, category, price, stock, sku))
            conn.commit()
            conn.close()
            return True, "Cập nhật thành công."
        except Exception as e:
            print(f"Lỗi cập nhật sản phẩm: {e}")
            return False, f"Lỗi CSDL: {e}"
    return False, "Lỗi kết nối CSDL."

def deleteProduct(sku):
    """'Xóa' sản phẩm dựa trên SKU bằng cách set tồn kho về 0."""
    conn = getDbConnection()
    if conn:
        try:
            cursor = conn.cursor()
            # THAY ĐỔI: UPDATE stockQuantity = 0 thay vì DELETE
            query = "UPDATE Products SET stockQuantity = 0 WHERE SKU = ?" 
            cursor.execute(query, (sku,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return False
            
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi 'xóa' sản phẩm: {e}")
            return False
    return False