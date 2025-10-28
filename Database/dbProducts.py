from .dbConnector import getDbConnection

# ----------------------------------------------------------------------
# --- HÀM TRUY VẤN VÀ TẢI DỮ LIỆU SẢN PHẨM ---
# ----------------------------------------------------------------------

def _format_product_row(row):
    """Hàm trợ giúp nội bộ để định dạng một dòng dữ liệu sản phẩm."""
    if not row: return None
    
    sku = row[0]
    name = row[1]
    category = row[2]
    price = row[3]
    stock = int(row[4])
    imagePath = row[5]
    description = row[6]
    
    # Định dạng giá (Price string)
    try:
        price_str = f"{float(price):,.0f}"
    except:
        price_str = str(price)
    
    # Định dạng lại các chuỗi (Xóa dấu nháy đơn nếu có)
    clean_name = name.strip("'") if isinstance(name, str) else name
    clean_category = category.strip("'") if isinstance(category, str) else category
    
    return (
        sku, 
        clean_name,
        clean_category,
        price_str, # Giá đã định dạng
        stock,
        imagePath if imagePath else '',
        description if description else ''
    )

def getAllProducts():
    """Lấy tất cả sản phẩm (bao gồm cả hàng hết kho) với định dạng giá."""
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        query = "SELECT SKU, name, category, price, stockQuantity, ImagePath, Description FROM Products"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            formatted_product = _format_product_row(row)
            if formatted_product:
                products.append(formatted_product)
            
    except Exception as e:
        print(f"Lỗi khi tải tất cả sản phẩm: {e}")
    finally:
        if conn:
            conn.close()
            
    return products

def getProductsForPOS():
    """Lấy sản phẩm CHỈ CÓ TỒN KHO > 0 (Dùng cho POSPage)."""
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        # LỌC: Chỉ lấy sản phẩm có stockQuantity > 0
        query = "SELECT SKU, name, category, price, stockQuantity, ImagePath, Description FROM Products WHERE stockQuantity > 0"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            # Định dạng giá riêng cho POS (thêm VNĐ)
            price = row[3]
            try:
                price_str = f"{float(price):,.0f} VNĐ"
            except:
                price_str = str(price)
            
            # Trả về 7 trường dữ liệu
            products.append((row[0], row[1], row[2], price_str, row[4], row[5], row[6])) 
            
    except Exception as e:
        print(f"Lỗi khi tải sản phẩm POS: {e}")
    finally:
        if conn:
            conn.close()
            
    return products

def getProductDetailBySku(sku):
    """Lấy thông tin chi tiết của một sản phẩm bằng SKU và trả về dưới dạng dictionary."""
    conn = getDbConnection()
    if not conn: return None
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description 
        FROM Products 
        WHERE SKU = ?
        """
        cursor.execute(query, (sku,))
        row = cursor.fetchone()
        
        if row:
            price = row[3]
            stock_quantity = int(row[4])
            
            # Định dạng giá cho hiển thị chi tiết
            try:
                price_str = f"{float(price):,.0f} VNĐ"
            except:
                price_str = str(price)
                
            return {
                "sku": row[0],
                "name": row[1],
                "category": row[2],
                "price": price,         # Giá trị số (dùng cho tính toán giỏ hàng)
                "price_str": price_str, # Giá trị chuỗi đã định dạng
                "quantity": stock_quantity,
                "imagePath": row[5] if row[5] else None,
                "description": row[6] if row[6] else "Không có mô tả chi tiết."
            }
        return None
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết sản phẩm: {e}")
        return None
    finally:
        if conn:
            conn.close()

# ----------------------------------------------------------------------
# --- HÀM THÊM, CẬP NHẬT & XÓA SẢN PHẨM ---
# ----------------------------------------------------------------------

def addProduct(sku, name, category, price, stock, imagePath=None, description=None):
    """Thêm sản phẩm mới hoặc cộng dồn tồn kho nếu tên sản phẩm đã tồn tại."""
    conn = getDbConnection()
    if not conn: return False, "Không thể kết nối CSDL."
        
    cursor = conn.cursor()
    name = name.strip()
    sku = sku.strip()
    
    # Chuẩn hóa giá trị None (NULL)
    imagePath = imagePath.strip() if imagePath and isinstance(imagePath, str) else None
    description = description.strip() if description and isinstance(description, str) else None
    
    if not sku: return False, "Mã SP (SKU) không được để trống."
    
    try:
        # 1. Kiểm tra TÊN SẢN PHẨM đã tồn tại
        cursor.execute("SELECT SKU, stockQuantity FROM Products WHERE name = ?", (name,))
        existing_by_name = cursor.fetchone()

        if existing_by_name:
            # Tên đã tồn tại: CẬP NHẬT TỒN KHO VÀ THÔNG TIN KHÁC
            product_sku_old = existing_by_name[0]
            current_stock = int(existing_by_name[1])
            new_stock = current_stock + stock
            
            sql_update = """
                UPDATE Products 
                SET category = ?, price = ?, stockQuantity = ?, ImagePath = ?, Description = ? 
                WHERE SKU = ? 
            """
            cursor.execute(sql_update, (category, price, new_stock, imagePath, description, product_sku_old))
            message = f"Sản phẩm '{name}' (SKU: {product_sku_old}) đã có. Đã cộng dồn {stock} đơn vị. Tồn kho mới: {new_stock}."
            
        else:
            # Tên mới: PHẢI kiểm tra SKU đã tồn tại chưa
            cursor.execute("SELECT SKU FROM Products WHERE SKU = ?", (sku,))
            if cursor.fetchone():
                return False, f"Lỗi: Mã sản phẩm (SKU) '{sku}' đã được sử dụng. Vui lòng chọn Mã khác."

            # Tên mới VÀ SKU mới: CHÈN SẢN PHẨM MỚI
            sql_insert = """
                INSERT INTO Products (SKU, name, category, price, stockQuantity, ImagePath, Description) 
                VALUES (?, ?, ?, ?, ?, ?, ?) 
            """
            cursor.execute(sql_insert, (sku, name, category, price, stock, imagePath, description))
            message = f"Đã thêm sản phẩm mới (SKU: {sku})."

        conn.commit()
        return True, message
        
    except Exception as e:
        print(f"LỖI THÊM/CẬP NHẬT SẢN PHẨM: {e}") 
        return False, f"Lỗi CSDL: {e}"
        
    finally:
        if conn:
            conn.close()

def updateProduct(sku, name, category, price, stock, imagePath=None, description=None):
    """Cập nhật toàn bộ thông tin sản phẩm dựa trên SKU."""
    conn = getDbConnection()
    if not conn: return False, "Lỗi kết nối CSDL."
        
    try:
        cursor = conn.cursor()
        name = name.strip()
        
        # Chuẩn hóa giá trị None (NULL)
        imagePath = imagePath.strip() if imagePath and isinstance(imagePath, str) else None
        description = description.strip() if description and isinstance(description, str) else None

        # Kiểm tra trùng tên (Trừ chính SKU đang sửa)
        cursor.execute("SELECT SKU FROM Products WHERE name = ? AND SKU != ?", (name, sku))
        if cursor.fetchone():
            return False, f"Lỗi: Tên sản phẩm '{name}' đã được sử dụng bởi SKU khác."

        query = """
        UPDATE Products 
        SET name = ?, category = ?, price = ?, stockQuantity = ?, ImagePath = ?, Description = ? 
        WHERE SKU = ?
        """
        # Truyền đủ 7 tham số theo đúng thứ tự
        cursor.execute(query, (name, category, price, stock, imagePath, description, sku))
        conn.commit()
        return True, "Cập nhật thành công."
        
    except Exception as e:
        print(f"Lỗi cập nhật sản phẩm: {e}")
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn:
            conn.close()

def deleteProduct(sku):
    """'Xóa' sản phẩm bằng cách set tồn kho về 0."""
    conn = getDbConnection()
    if not conn: return False
        
    try:
        cursor = conn.cursor()
        query = "UPDATE Products SET stockQuantity = 0 WHERE SKU = ?" 
        cursor.execute(query, (sku,))
        conn.commit()
        
        return cursor.rowcount > 0 # True nếu có ít nhất 1 dòng bị ảnh hưởng
            
    except Exception as e:
        print(f"Lỗi 'xóa' sản phẩm (set stock=0): {e}")
        return False
    finally:
        if conn:
            conn.close()

def searchProducts(keyword):
    """Tìm kiếm sản phẩm theo Tên (name) hoặc Mã SP (SKU) và trả về danh sách định dạng."""
    conn = getDbConnection()
    formatted_products = []
    if not conn: return []
    cursor = conn.cursor()
    
    try:
        # Tìm kiếm theo tên HOẶC SKU (sử dụng LIKE và dấu %)
        sql_query = """
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description 
        FROM Products 
        WHERE name LIKE ? OR SKU LIKE ?
        """
        search_term = '%' + keyword.strip() + '%'
        
        cursor.execute(sql_query, search_term, search_term)
        rows = cursor.fetchall()
        
        # Định dạng lại dữ liệu trước khi trả về
        for row in rows:
            formatted_product = _format_product_row(row)
            if formatted_product:
                formatted_products.append(formatted_product)
        
        return formatted_products
        
    except Exception as e:
        print(f"Lỗi khi tìm kiếm sản phẩm: {e}")
        return []
    finally:
        if conn:
            conn.close()

# ----------------------------------------------------------------------
# --- HÀM CẬP NHẬT TỒN KHO ĐỘC LẬP (Dùng cho POS) ---
# ----------------------------------------------------------------------

def updateStockQuantity(sku, quantity_change):
    """
    Cập nhật tồn kho sản phẩm (TRỪ số lượng khi bán).
    :param quantity_change: Số lượng cần TRỪ đi.
    """
    conn = getDbConnection()
    if not conn: return False, "Lỗi kết nối CSDL."
    cursor = conn.cursor()
    
    try:
        # 1. Kiểm tra tồn kho hiện tại (Dùng khóa để đảm bảo an toàn nếu là môi trường đa luồng)
        cursor.execute("SELECT stockQuantity FROM Products WHERE SKU = ?", (sku,))
        result = cursor.fetchone()
        
        if not result:
            return False, f"Lỗi: Không tìm thấy sản phẩm với SKU '{sku}'."
            
        current_stock = int(result[0])
        new_stock = current_stock - quantity_change
        
        if new_stock < 0:
            # Không commit/rollback vì chưa có giao dịch
            return False, f"Lỗi: Tồn kho hiện tại ({current_stock}) không đủ để bán {quantity_change} đơn vị."

        # 2. Cập nhật tồn kho mới
        cursor.execute("""
            UPDATE Products 
            SET stockQuantity = ?
            WHERE SKU = ?
        """, (new_stock, sku))
        
        conn.commit()
        return True, "Cập nhật tồn kho thành công."
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi cập nhật tồn kho: {e}")
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn:
            conn.close()