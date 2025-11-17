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

def getAllProductsForAdmin():
    """
    Lấy TẤT CẢ sản phẩm (kể cả đã Ngừng kinh doanh) để hiển thị trên Admin Page, 
    bao gồm cả trạng thái isActive. Trả về danh sách dictionary.
    """
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        query = "SELECT SKU, name, category, price, stockQuantity, ImagePath, Description, isActive FROM Products"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            # 1. Định dạng giá 
            price = row[3]
            try:
                price_str = f"{float(price):,.0f}"
            except:
                price_str = str(price)
            
            # 2. Xử lý trạng thái
            is_active_int = int(row[7])
            status_text = "Đang kinh doanh" if is_active_int == 1 else "Ngừng kinh doanh"
            
            products.append({
                'SKU': row[0],
                'name': row[1].strip("'") if isinstance(row[1], str) else row[1],
                'category': row[2].strip("'") if isinstance(row[2], str) else row[2],
                'price': price_str,
                'stock': row[4],
                'imagePath': row[5] if row[5] else '',
                'description': row[6] if row[6] else '',
                'isActive': is_active_int,
                'status_text': status_text
            })
            
    except Exception as e:
        print(f"Lỗi khi tải tất cả sản phẩm cho Admin: {e}")
    finally:
        if conn:
            conn.close()
            
    return products

def getProductsForPOS():
    """
    Lấy tất cả sản phẩm đang hoạt động (isActive = 1) để hiển thị bên POSPage.
    Sản phẩm hết hàng (stock=0) vẫn được hiển thị.
    """
    conn = getDbConnection()
    if not conn: return []
    cursor = conn.cursor()
    products = []
    
    try:
        # LỌC: Chỉ lấy sản phẩm có isActive = 1
        query = "SELECT SKU, name, category, price, stockQuantity, ImagePath, Description FROM Products WHERE isActive = 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            # Định dạng giá riêng cho POS (thêm VNĐ)
            price = row[3]
            price_float = 0 # Khởi tạo giá trị mặc định cho price_float
            try:
                price_float = float(price) # Giá trị số
                price_str = f"{price_float:,.0f} VNĐ"
            except:
                price_str = str(price) + " (Lỗi Giá)" # Giá trị chuỗi báo lỗi nếu cần
            
            # Trả về 7 trường dữ liệu
            products.append({
                'sku': row[0],
                'name': row[1].strip("'") if isinstance(row[1], str) else row[1],
                'category': row[2].strip("'") if isinstance(row[2], str) else row[2],
                'price_str': price_str,            # Dùng để hiển thị
                'price': price_float,              # Dùng để tính giỏ hàng (sử dụng 0 nếu lỗi)
                'stock': int(row[4]),
                'imagePath': row[5] if row[5] else '', # Lấy đúng index 5 (ImagePath)
                'description': row[6] if row[6] else ''
            })
            
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
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description, isActive 
        FROM Products 
        WHERE SKU = ?
        """
        cursor.execute(query, (sku,))
        row = cursor.fetchone()
        
        if row:
            price = row[3]
            stock_quantity = int(row[4])
            is_active = int(row[7])
            
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
                "description": row[6] if row[6] else "Không có mô tả chi tiết.",
                "isActive": is_active
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

def discontinueProduct(sku):
    """
    'Ngừng kinh doanh' sản phẩm bằng cách set isActive = 0.
    """
    conn = getDbConnection()
    if not conn: return False, "Lỗi kết nối CSDL."
        
    try:
        cursor = conn.cursor()
        # Set isActive = 0
        query = "UPDATE Products SET isActive = 0 WHERE SKU = ?" 
        cursor.execute(query, (sku,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, f"Sản phẩm {sku} đã ngừng kinh doanh thành công."
        else:
            return False, f"Không tìm thấy sản phẩm có Mã: {sku}."
            
    except Exception as e:
        print(f"Lỗi khi Ngừng kinh doanh sản phẩm: {e}")
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn:
            conn.close()

def removeProductPermanently(sku):
    """
    Xóa sản phẩm khỏi CSDL (xóa hoàn toàn) CHỈ KHI isActive = 0.
    Xử lý lỗi Khóa ngoại bằng cách xóa OrderItems liên quan trước.
    """
    conn = getDbConnection()
    if not conn: 
        return False, "Không thể kết nối CSDL."
    cursor = conn.cursor()
    
    try:
        # 1. KIỂM TRA TRẠNG THÁI KINH DOANH (isActive) TRƯỚC KHI XÓA
        cursor.execute("SELECT isActive FROM Products WHERE SKU = ?", (sku,))
        result = cursor.fetchone()
        
        if not result:
            return False, f"Không tìm thấy sản phẩm có Mã SP {sku}."
            
        is_active = int(result[0])
        
        # CHỈ CHO PHÉP XÓA KHI isActive = 0
        if is_active == 1:
            return False, f"Không thể xóa vĩnh viễn. Sản phẩm này đang hoạt động. Vui lòng sử dụng nút 'Xóa' (Dừng kinh doanh) trước."

        # 2. XÓA BẢN GHI LIÊN QUAN TRONG BẢNG ORDERITEMS (Xóa Thác)
        cursor.execute("DELETE FROM OrderItems WHERE SKU = ?", (sku,))
        rows_deleted_orderitems = cursor.rowcount 

        # 3. XÓA SẢN PHẨM KHỎI BẢNG PRODUCTS
        cursor.execute("DELETE FROM Products WHERE SKU = ?", (sku,))
        rows_deleted_products = cursor.rowcount

        conn.commit()
        
        if rows_deleted_products > 0:
            msg = f"Đã xóa vĩnh viễn sản phẩm {sku} thành công."
            if rows_deleted_orderitems > 0:
                msg += f" (Đồng thời xóa {rows_deleted_orderitems} mục lịch sử đơn hàng liên quan)."
            return True, msg
        else:
            return False, f"Không tìm thấy sản phẩm có Mã SP {sku} để xóa."

    except Exception as e:
        conn.rollback()
        print(f"LỖI CSDL KHI XÓA VĨNH VIỄN: {e}")
        return False, f"Lỗi CSDL khi xóa vĩnh viễn: {e}"
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

def resumeProduct(sku):
    """
    'Kinh doanh lại' sản phẩm bằng cách set isActive = 1.
    """
    conn = getDbConnection()
    if not conn: return False, "Lỗi kết nối CSDL."
        
    try:
        cursor = conn.cursor()
        # Set isActive = 1
        query = "UPDATE Products SET isActive = 1 WHERE SKU = ?" 
        cursor.execute(query, (sku,))
        conn.commit()
        
        if cursor.rowcount > 0:
             return True, f"Đã kích hoạt kinh doanh lại sản phẩm {sku}."
        else:
             return False, f"Không tìm thấy sản phẩm {sku} để kích hoạt."
            
    except Exception as e:
        print(f"Lỗi khi Kinh doanh lại sản phẩm: {e}")
        return False, f"Lỗi CSDL: {e}"
    finally:
        if conn:
            conn.close()

    # (THÊM HÀM NÀY VÀO CUỐI FILE  để tìm kiếm  dbProducts.py)

def searchProductsForPOS(keyword):
    """
    Tìm kiếm sản phẩm (theo Tên hoặc SKU) CHỈ LẤY CÁC SẢN PHẨM CÒN KINH DOANH (isActive=1)
    và trả về định dạng dictionary giống hệt getProductsForPOS.
    """
    conn = getDbConnection()
    products = []
    if not conn: return []
    cursor = conn.cursor()
    
    try:
        # SỬA ĐỔI: Thêm "AND isActive = 1"
        sql_query = """
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description 
        FROM Products 
        WHERE (name LIKE ? OR SKU LIKE ?) AND isActive = 1 
        """
        # Thêm dấu % cho tìm kiếm LIKE
        search_term = '%' + keyword.strip() + '%'
        
        cursor.execute(sql_query, (search_term, search_term))
        rows = cursor.fetchall()
        
        # SAO CHÉP LOGIC ĐỊNH DẠNG TỪ getProductsForPOS
        for row in rows:
            price = row[3]
            price_float = 0 
            try:
                price_float = float(price) 
                price_str = f"{price_float:,.0f} VNĐ"
            except:
                price_str = str(price) + " (Lỗi Giá)"
            
            products.append({
                'sku': row[0],
                'name': row[1].strip("'") if isinstance(row[1], str) else row[1],
                'category': row[2].strip("'") if isinstance(row[2], str) else row[2],
                'price_str': price_str,     # Dùng để hiển thị
                'price': price_float,       # Dùng để tính giỏ hàng
                'stock': int(row[4]),
                'imagePath': row[5] if row[5] else '',
                'description': row[6] if row[6] else ''
            })
            
    except Exception as e:
        print(f"Lỗi khi tìm kiếm sản phẩm POS: {e}")
        return []
    finally:
        if conn:
            conn.close()
    return products

# thêm danh mục 
# (THÊM VÀO CUỐI FILE dbProducts.py)

def getAllCategories():
    """
    Lấy danh sách tất cả các danh mục (category) duy nhất đang kinh doanh (isActive=1).
    """
    conn = getDbConnection()
    categories = []
    if not conn: return []
    cursor = conn.cursor()
    
    try:
        # Lấy các danh mục duy nhất, không trùng lặp, bỏ qua NULL và lọc theo isActive=1
        query = """
        SELECT DISTINCT category 
        FROM Products 
        WHERE category IS NOT NULL AND category != '' AND isActive = 1
        ORDER BY category
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        # Chuyển đổi từ list of tuples [('Vang Đỏ',), ('Vang Trắng',)] sang list ['Vang Đỏ', 'Vang Trắng']
        categories = [row[0] for row in rows]
            
    except Exception as e:
        print(f"Lỗi khi lấy danh mục: {e}")
    finally:
        if conn:
            conn.close()
    return categories

def getProductsByCategoryForPOS(category):
    """
    Lấy tất cả sản phẩm thuộc một danh mục (category) cụ thể
    và trả về định dạng dictionary giống hệt getProductsForPOS.
    """
    conn = getDbConnection()
    products = []
    if not conn: return []
    cursor = conn.cursor()
    
    try:
        # Lọc theo category và isActive = 1
        query = """
        SELECT SKU, name, category, price, stockQuantity, ImagePath, Description 
        FROM Products 
        WHERE category = ? AND isActive = 1
        """
        cursor.execute(query, (category,))
        rows = cursor.fetchall()
        
        # Sao chép logic định dạng từ getProductsForPOS
        for row in rows:
            price = row[3]
            price_float = 0 
            try:
                price_float = float(price) 
                price_str = f"{price_float:,.0f} VNĐ"
            except:
                price_str = str(price) + " (Lỗi Giá)"
            
            products.append({
                'sku': row[0],
                'name': row[1].strip("'") if isinstance(row[1], str) else row[1],
                'category': row[2].strip("'") if isinstance(row[2], str) else row[2],
                'price_str': price_str,
                'price': price_float,
                'stock': int(row[4]),
                'imagePath': row[5] if row[5] else '',
                'description': row[6] if row[6] else ''
            })
            
    except Exception as e:
        print(f"Lỗi khi lấy sản phẩm theo danh mục: {e}")
    finally:
        if conn:
            conn.close()
    return products