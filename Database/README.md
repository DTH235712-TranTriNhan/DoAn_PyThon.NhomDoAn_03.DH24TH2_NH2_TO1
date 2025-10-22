🛠️ Hướng Dẫn Thiết Lập Cơ Sở Dữ Liệu (SQL Server)
File này hướng dẫn cách tạo database và các bảng cần thiết để ứng dụng Python hoạt động.

1. Yêu Cầu Thiết Lập
```
SQL Server: Đã cài đặt SQL Server và SQL Server Management Studio (SSMS).

Tên Server: Đảm bảo bạn biết tên Server của mình (ví dụ: LAPTOP-L0M5...\SQLEXPRESS).

chạy lệnh này để kết nối Vscode với sql service
pip install pyodbc
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
USE salesProjectDB;
GO
```

B. Tạo Bảng Cấu trúc (4 Bảng)
1. Bảng Users (Người dùng & Phân quyền)
```sql
-- Sử dụng IDENTITY cho ID tự động tăng và NVARCHAR cho tiếng Việt có dấu.
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
2. Bảng Products (Hàng hóa & Tồn kho)
```sql
CREATE TABLE Products (
    SKU VARCHAR(50) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE, 
    category NVARCHAR(100), 
    price DECIMAL(18, 0) NOT NULL,
    stockQuantity INT NOT NULL DEFAULT 0,
    ImagePath NVARCHAR(MAX),
    Description NVARCHAR(MAX)
);
```
3. Bảng Orders (Đơn hàng/Hóa đơn)
```sql
CREATE TABLE Orders (
    orderID INT IDENTITY(1,1) PRIMARY KEY,
    userID VARCHAR(50),                     -- Khóa ngoại phải khớp với Users.userID (VARCHAR)
    orderDate DATETIME NOT NULL DEFAULT GETDATE(),
    totalAmount DECIMAL(18, 0) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    FOREIGN KEY (userID) REFERENCES Users(userID) -- Khóa ngoại trỏ đến Users.userID mới
);
```
4. Bảng OrderItems (Chi tiết Đơn hàng)
```sql
CREATE TABLE OrderItems (
    itemID INT IDENTITY(1,1) PRIMARY KEY,
    orderID INT NOT NULL,   
    SKU VARCHAR(50) NOT NULL,      -- Tự nhập (Mã sản phẩm)
    quantity INT NOT NULL,
    unitPrice DECIMAL(18, 0) NOT NULL,
    FOREIGN KEY (orderID) REFERENCES Orders(orderID),
    FOREIGN KEY (SKU) REFERENCES Products(SKU)
);
```
C. Dữ liệu Khởi tạo (Mặc định)
```sql
-- Chèn tài khoản Admin và Guest để kiểm tra đăng nhập.
-- Chèn tài khoản Admin và Guest.
INSERT INTO Users (userID, userName, password, fullName, userRole) VALUES
('AD001', 'admin', '123', N'Quản trị viên Hệ thống', 'Admin'),
('GT001', 'guest', '123', N'Khách Vãng Lai', 'Guest');
```
3. Cấu Hình Kết Nối Python
```sql
-- Sau khi tạo Database, bạn phải kiểm tra và sửa đổi tên Server trong file Database/dbConnector.py:
# Mở file databaseManager.py và sửa dòng này:
# Lưu ý: Phải thêm chữ 'r' để tránh lỗi cú pháp \ trong Python
SERVER_NAME = r'TEN_SERVER_CUA_BAN\SQLEXPRESS'
```


Trường hợp 2: SQL Server Authentication (Cần Tên/Mật khẩu SQL)
```sql
-- Cách Sửa trong Database/dbConnector.py (Dành cho người dùng khác):
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