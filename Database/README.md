# 🛠️ HƯỚNG DẪN THIẾT LẬP CƠ SỞ DỮ LIỆU (SQL SERVER)

File này hướng dẫn cách tạo database và các bảng cần thiết để ứng dụng Python hoạt động.

---

## 1. YÊU CẦU THIẾT LẬP
```
SQL Server: Đã cài đặt SQL Server và SQL Server Management Studio (SSMS).

Tên Server: Đảm bảo bạn biết tên Server của mình (ví dụ: LAPTOP-XXXX\SQLEXPRESS).

Chạy lệnh này để cài thư viện kết nối VSCode với SQL Server:
```

```
pip install pyodbc
pip install Pillow
```

---

## 2. CÁC BƯỚC TẠO DATABASE
```
Mở SQL Server Management Studio (SSMS), tạo một cửa sổ New Query, và chạy toàn bộ các lệnh dưới đây theo thứ tự:
```

### A. Tạo Database và chuyển ngữ cảnh
```sql
-- Tên Database (Dùng CamelCase: salesProjectDB)
CREATE DATABASE salesProjectDB;
GO 

USE salesProjectDB;
GO
```

---

## B. Tạo Bảng Cấu Trúc (4 bảng)

### 1. Bảng Users (Người dùng & Phân quyền)
```sql
-- Sử dụng NVARCHAR cho tiếng Việt và CHECK cho phân quyền.
CREATE TABLE Users (
    userID VARCHAR(50) PRIMARY KEY,
    userName VARCHAR(50) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL,
    fullName NVARCHAR(100), 
    phone VARCHAR(20),
    address NVARCHAR(255), 
    userRole VARCHAR(10) NOT NULL,
    
    CONSTRAINT CHK_UserRole CHECK (userRole IN ('Admin', 'User', 'Guest'))
);
```

### 2. Bảng Products (Hàng hóa & Tồn kho)
```sql
CREATE TABLE Products (
    SKU VARCHAR(50) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE, 
    category NVARCHAR(100), 
    price DECIMAL(18, 0) NOT NULL,
    stockQuantity INT NOT NULL DEFAULT 0,
    ImagePath NVARCHAR(MAX),
    Description NVARCHAR(MAX),
    isActive BIT NOT NULL DEFAULT 1
);
```

### 3. Bảng Orders (Đơn hàng)
```sql
CREATE TABLE Orders (
    orderID INT IDENTITY(1,1) PRIMARY KEY,
    userID VARCHAR(50),
    orderDate DATETIME NOT NULL DEFAULT GETDATE(),
    totalAmount DECIMAL(18, 0) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Completed',

    FOREIGN KEY (userID) REFERENCES Users(userID)
);
```

### 4. Bảng OrderItems (Chi tiết đơn hàng)
```sql
CREATE TABLE OrderItems (
    itemID INT IDENTITY(1,1) PRIMARY KEY,
    orderID INT NOT NULL,
    SKU VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unitPrice DECIMAL(18, 0) NOT NULL,

    FOREIGN KEY (orderID) REFERENCES Orders(orderID),
    FOREIGN KEY (SKU) REFERENCES Products(SKU)
);
```

---

## C. DỮ LIỆU KHỞI TẠO (ADMIN & GUEST)
```sql
INSERT INTO Users (userID, userName, password, fullName, userRole) VALUES
('AD001', 'admin', '123', N'Quản trị viên Hệ thống', 'Admin'),
('GT001', 'guest', '123', N'Khách Vãng Lai', 'Guest');
```

---

## 3. CẤU HÌNH KẾT NỐI PYTHON

Trong file `dbConnector.py` sửa:
```python
# Lưu ý: Thêm chữ r'' để tránh lỗi escape ký tự \
SERVER_NAME = r'TEN_SERVER_CUA_BAN\SQLEXPRESS'
```

---

## Trường hợp 2: SQL Server Authentication (Dùng user + password SQL)

```python
# Cách sửa trong dbConnector.py
def checkLogin(username, password):

    # !!! NGƯỜI DÙNG CẦN SỬA DÒNG NÀY !!!
    # Ví dụ: user="sa", password="matkhaucuaban"
    conn = getDbConnection(
        user="TEN_SQL_USER",
        password="MAT_KHAU_SQL"
    )

    # ... logic truy vấn ...
```

```
Lưu ý:
- Nếu dùng SQL Authentication, bạn phải bật Mixed Mode trong SQL Server.
- Bật giao thức TCP/IP trong SQL Server Configuration Manager.
```

---

✔️ Mọi thứ đã sẵn sàng để chạy dự án Python kết nối SQL Server!
