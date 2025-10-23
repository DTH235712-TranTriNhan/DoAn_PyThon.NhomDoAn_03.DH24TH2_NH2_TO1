from .dbConnector import getDbConnection

def getAllProducts():
    """Lấy tất cả sản phẩm có tồn kho > 0 và sử dụng SKU làm ID."""
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        # THAY ĐỔI: Chọn SKU thay vì productID và lọc stockQuantity > 0
        cursor.execute("SELECT SKU, name, category, price, stockQuantity, ImagePath, Description FROM Products")
        rows = cursor.fetchall()
        
        for row in rows:
            sku = row[0]
            name = row[1]
            category = row[2]
            price = row[3]
            stock = int(row[4])
            imagePath = row[5]
            description = row[6]
            
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
                stock,
                imagePath if imagePath else '',
                description if description else ''
            )
            products.append(formatted_product)
            
    except Exception as e:
        print(f"Lỗi khi tải sản phẩm: {e}")
    finally:
        if conn:
            conn.close()
        
    return products

def addProduct(sku, name, category, price, stock, imagePath=None, description=None):
    """Thêm/Cập nhật sản phẩm với đầy đủ thông tin (kèm ảnh và mô tả)."""
    conn = getDbConnection()
    if not conn: return False, "Không thể kết nối CSDL."
        
    cursor = conn.cursor()
    name = name.strip()
    sku = sku.strip()
    
    # Chuẩn hóa giá trị: Gửi None (NULL) nếu chuỗi rỗng
    imagePath = imagePath.strip() if imagePath and isinstance(imagePath, str) else None
    description = description.strip() if description and isinstance(description, str) else None
    
    if not sku: return False, "Mã SP (SKU) không được để trống."
    
    try:
        # 1. KIỂM TRA TRÙNG TÊN SẢN PHẨM (Ưu tiên: Cộng dồn)
        cursor.execute("SELECT SKU, stockQuantity FROM Products WHERE name = ?", (name,)) # Thêm (name,)
        existing_by_name = cursor.fetchone()

        if existing_by_name:
            # Tên đã tồn tại: CẬP NHẬT TỒN KHO VÀ THÔNG TIN (Dùng SKU cũ)
            product_sku_old = existing_by_name[0]
            current_stock = existing_by_name[1]
            new_stock = current_stock + stock
            
            sql_update = """
                UPDATE Products 
                SET category = ?, price = ?, stockQuantity = ?, ImagePath = ?, Description = ? 
                WHERE SKU = ? 
            """
            # Cung cấp đủ 6 tham số
            cursor.execute(sql_update, (category, price, new_stock, imagePath, description, product_sku_old))
            message = f"Sản phẩm '{name}' (SKU: {product_sku_old}) đã có. Đã cộng dồn {stock} đơn vị. Tồn kho mới: {new_stock}."
            
        else:
            # Tên mới: Phải kiểm tra SKU đã tồn tại chưa
            cursor.execute("SELECT SKU FROM Products WHERE SKU = ?", (sku,))
            if cursor.fetchone():
                return False, f"Lỗi: Mã sản phẩm (SKU) '{sku}' đã được sử dụng. Vui lòng chọn Mã khác."

            # Tên mới VÀ SKU mới: CHÈN
            sql_insert = """
                INSERT INTO Products (SKU, name, category, price, stockQuantity, ImagePath, Description) 
                VALUES (?, ?, ?, ?, ?, ?, ?) 
            """
            # Cung cấp đủ 7 tham số
            cursor.execute(sql_insert, (sku, name, category, price, stock, imagePath, description))
            message = f"Đã thêm sản phẩm mới (SKU: {sku})."

        conn.commit()
        return True, message
        
    except Exception as e:
        # In lỗi chi tiết để dễ debug
        print(f"LỖI CHI TIẾT KHI THÊM/CẬP NHẬT SẢN PHẨM: {e}") 
        return False, f"Lỗi CSDL: {e}"
        
    finally:
        if conn:
            conn.close()

def getProductDetailBySku(sku):
    """Lấy thông tin chi tiết của một sản phẩm bằng SKU (Đã bao gồm ImagePath và Description)."""
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
            try:
                price_str = f"{float(price):,.0f} VNĐ"
            except:
                price_str = str(price)
                
            product_detail = {
                "sku": row[0],
                "name": row[1],
                "category": row[2],
                "price_str": price_str,
                "stock": int(row[4]),
                # Lấy 2 trường mới:
                "imagePath": row[5] if row[5] else None,
                "description": row[6] if row[6] else "Không có mô tả chi tiết."
            }
            return product_detail
        return None
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết sản phẩm: {e}")
        return None
    finally:
        if conn:
            conn.close()

def updateProduct(sku, name, category, price, stock, imagePath=None, description=None):
    """Cập nhật thông tin sản phẩm dựa trên SKU (Bao gồm ImagePath và Description)."""
    conn = getDbConnection()
    if conn:
        try:
            cursor = conn.cursor()
            name = name.strip()
            
            # Chuẩn hóa giá trị: Gửi None (NULL) nếu chuỗi rỗng
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
            # Sửa: Truyền đủ 7 tham số theo đúng thứ tự (Name, Category, Price, Stock, ImagePath, Description, SKU)
            cursor.execute(query, (name, category, price, stock, imagePath, description, sku))
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

def searchProducts(keyword):
    """
    Tìm kiếm sản phẩm theo Tên (name) hoặc Mã SP (SKU).
    Trả về danh sách các tuple sản phẩm ĐÃ ĐỊNH DẠNG.
    """
    conn = None
    formatted_products = []
    try:
        conn = getDbConnection() # SỬ DỤNG HÀM CÓ SẴN
        if not conn: return []
        cursor = conn.cursor()
        
        # Tìm kiếm theo tên HOẶC SKU (sử dụng LIKE và dấu %)
        sql_query = """
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description 
        FROM Products 
        WHERE name LIKE ? OR SKU LIKE ?
        """
        # Thêm dấu % vào keyword để tìm kiếm chuỗi con
        search_term = '%' + keyword.strip() + '%'
        
        cursor.execute(sql_query, search_term, search_term)
        rows = cursor.fetchall()
        
        # Định dạng lại dữ liệu trước khi trả về (giống getAllProducts)
        for row in rows:
            sku = row[0]
            name = row[1]
            category = row[2]
            price = row[3]
            stock = int(row[4])
            imagePath = row[5]
            description = row[6]
            
            # Format giá
            try:
                # Sử dụng .0f vì DECIMAL(18, 0)
                price_str = f"{float(price):,.0f}" 
            except:
                price_str = str(price)
            
            formatted_product = (
                sku, 
                name.strip("'") if isinstance(name, str) else name,
                category.strip("'") if isinstance(category, str) else category,
                price_str, # Giá đã được định dạng
                stock,
                imagePath if imagePath else '', 
                description if description else ''
            )
            formatted_products.append(formatted_product)
        
        return formatted_products
        
    except Exception as e:
        print(f"Lỗi khi tìm kiếm sản phẩm: {e}")
        return []
    finally:
        if conn:
            conn.close()

def getProductDetailBySku(sku):
    """Lấy thông tin chi tiết của một sản phẩm bằng SKU."""
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
            # Định dạng giá trị giống như getAllProducts
            price = row[3]
            try:
                price_str = f"{float(price):,.0f} VNĐ"
            except:
                price_str = str(price)
                
            product_detail = {
                "sku": row[0],
                "name": row[1],
                "category": row[2],
                "price_str": price_str,
                "stock": int(row[4]),
                "imagePath": row[5] if row[5] else None,
                "description": row[6] if row[6] else "Không có mô tả chi tiết."
            }
            return product_detail
        return None
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết sản phẩm: {e}")
        return None
    finally:
        if conn:
            conn.close()