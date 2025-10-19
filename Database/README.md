🛠️ Hướng Dẫn Thiết Lập Cơ Sở Dữ Liệu (SQL Server)
File này hướng dẫn cách tạo database và các bảng cần thiết để ứng dụng Python hoạt động.

1. Yêu Cầu Thiết Lập
```
SQL Server: Đã cài đặt SQL Server và SQL Server Management Studio (SSMS).

Tên Server: Đảm bảo bạn biết tên Server của mình (ví dụ: LAPTOP-L0M5...\SQLEXPRESS).
```
2. Các Bước Tạo Database
```
Mở SQL Server Management Studio (SSMS), tạo một cửa sổ New Query, và chạy toàn bộ các lệnh SQL dưới đây theo thứ tự:
```
A. Tạo Database và Chọn Ngữ cảnh
```sql
-- Tên Database (Dùng CamelCase: salesProjectDB)
CREATE DATABASE salesProjectDB;
GO 
-- Chọn Database để tạo bảng
USE salesProjectDB;
GO
```

B. Tạo Bảng Cấu trúc (4 Bảng)
1. Bảng Users (Người dùng & Phân quyền)
```sql
-- Sử dụng IDENTITY cho ID tự động tăng và NVARCHAR cho tiếng Việt có dấu.
CREATE TABLE Users (
    userID INT IDENTITY(1,1) PRIMARY KEY,
    userName VARCHAR(50) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL,
    fullName NVARCHAR(100), -- Hỗ trợ tiếng Việt có dấu
    phone VARCHAR(20),
    address NVARCHAR(255),  -- Hỗ trợ tiếng Việt có dấu
    userRole VARCHAR(10) NOT NULL,
    
    CONSTRAINT CHK_UserRole CHECK (userRole IN ('admin', 'user', 'guest'))
);
```
2. Bảng Products (Hàng hóa & Tồn kho)
```sql
CREATE TABLE Products (
    productID INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL, -- Tên sản phẩm có dấu
    category NVARCHAR(100), -- Danh mục có dấu
    price DECIMAL(10, 2) NOT NULL,
    stockQuantity INT NOT NULL DEFAULT 0
);
```
3. Bảng Orders (Đơn hàng/Hóa đơn)
```sql
CREATE TABLE Orders (
    orderID INT IDENTITY(1,1) PRIMARY KEY,
    userID INT, 
    orderDate DATETIME NOT NULL DEFAULT GETDATE(),
    totalAmount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    FOREIGN KEY (userID) REFERENCES Users(userID)
);
```
4. Bảng OrderItems (Chi tiết Đơn hàng)
```sql
CREATE TABLE OrderItems (
    itemID INT IDENTITY(1,1) PRIMARY KEY,
    orderID INT NOT NULL,
    productID INT NOT NULL,
    quantity INT NOT NULL,
    unitPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (orderID) REFERENCES Orders(orderID),
    FOREIGN KEY (productID) REFERENCES Products(productID)
);
```
C. Dữ liệu Khởi tạo (Mặc định)
```sql
-- Chèn tài khoản Admin và Guest để kiểm tra đăng nhập.
INSERT INTO Users (userName, password, fullName, userRole) VALUES
('admin', 'admin123', N'Quản trị viên Hệ thống', 'admin'),
('guest', '123', N'Khách Vãng Lai', 'guest');
```
3. Cấu Hình Kết Nối Python
```sql
-- Sau khi tạo Database, bạn phải kiểm tra và sửa đổi tên Server trong file databaseManager.py:
# Mở file databaseManager.py và sửa dòng này:
# Lưu ý: Phải thêm chữ 'r' để tránh lỗi cú pháp \ trong Python
SERVER_NAME = r'TEN_SERVER_CUA_BAN\SQLEXPRESS'
```


Trường hợp 2: SQL Server Authentication (Cần Tên/Mật khẩu SQL)
```sql
-- Cách Sửa trong databaseManager.py (Dành cho người dùng khác):
def checkLogin(username, password):
    # !!! NGƯỜI DÙNG CẦN SỬA DÒNG NÀY !!!
    # Thay getDbConnection() bằng cách truyền user và password CSDL của họ
    # Ví dụ: user="sa", password="matkhaucuasa"
    
    # ⚠️ THAY DÒNG DƯỚI ĐÂY:
    conn = getDbConnection(user="TÊN_SQL_USER", password="MẬT_KHẨU_SQL") 
    
    # ... logic truy vấn ...
    # ...

-- Lưu ý: Nếu người dùng của bạn chọn Chế độ SQL Server Authentication, họ phải đảm bảo rằng server đã được cấu hình sang Mixed Mode và giao thức TCP/IP đã được bật.
```