-- 商品テーブル
CREATE TABLE IF NOT EXISTS `mydataset.products` (
  product_id STRING NOT NULL,
  sku STRING,
  name STRING,
  category STRING,
  brand STRING,
  price NUMERIC,
  currency STRING,
  active BOOL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 在庫テーブル
CREATE TABLE IF NOT EXISTS `mydataset.inventory` (
  product_id STRING NOT NULL,
  warehouse_id STRING,
  quantity INT64,
  safety_stock INT64,
  reorder_point INT64,
  incoming_qty INT64,
  status STRING,
  location STRING,
  lot_number STRING,
  updated_at TIMESTAMP
);

-- 売上テーブル（受注明細）
CREATE TABLE IF NOT EXISTS `mydataset.sales` (
  order_id STRING NOT NULL,
  order_item_id STRING NOT NULL,
  order_date TIMESTAMP,
  customer_id STRING,
  product_id STRING,
  quantity INT64,
  unit_price NUMERIC,
  discount NUMERIC,
  tax_amount NUMERIC,
  total_amount NUMERIC,
  currency STRING,
  status STRING
);

-- products: 10件
INSERT INTO `mydataset.products` (
  product_id, sku, name, category, brand, price, currency, active, created_at, updated_at
) VALUES
('P001','SKU-001','Basic T-Shirt','Apparel','Acme',19.99,'JPY',TRUE, TIMESTAMP '2025-10-01 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P002','SKU-002','Premium Hoodie','Apparel','Acme',59.00,'JPY',TRUE, TIMESTAMP '2025-10-02 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P003','SKU-003','Running Shoes','Footwear','RoadRunner',89.50,'JPY',TRUE, TIMESTAMP '2025-10-03 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P004','SKU-004','Socks 3-Pack','Apparel','Acme',9.99,'JPY',TRUE, TIMESTAMP '2025-10-04 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P005','SKU-005','Water Bottle 1L','Accessories','Hydra',14.20,'JPY',TRUE, TIMESTAMP '2025-10-05 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P006','SKU-006','Backpack 20L','Bags','TrailCo',39.80,'JPY',TRUE, TIMESTAMP '2025-10-06 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P007','SKU-007','Wireless Earbuds','Electronics','Soundly',129.00,'JPY',TRUE, TIMESTAMP '2025-10-07 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P008','SKU-008','Fitness Tracker','Electronics','Pulse',79.90,'JPY',TRUE, TIMESTAMP '2025-10-08 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P009','SKU-009','Yoga Mat','Sports','Flexi',24.00,'JPY',TRUE, TIMESTAMP '2025-10-09 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00'),
('P010','SKU-010','Cycling Helmet','Sports','RideSafe',99.00,'JPY',TRUE, TIMESTAMP '2025-10-10 09:00:00+00', TIMESTAMP '2025-10-10 12:00:00+00');

-- inventory: 10件
INSERT INTO `mydataset.inventory` (
  product_id, warehouse_id, quantity, safety_stock, reorder_point, incoming_qty, status, location, lot_number, updated_at
) VALUES
('P001','W1',120,20,50,30,'IN_STOCK','Tokyo','LOT-A1',TIMESTAMP '2025-10-10 12:00:00+00'),
('P002','W1',45,10,30,20,'IN_STOCK','Tokyo','LOT-A2',TIMESTAMP '2025-10-10 12:00:00+00'),
('P003','W2',15,10,25,40,'LOW','Osaka','LOT-B1',TIMESTAMP '2025-10-10 12:00:00+00'),
('P004','W1',300,30,100,0,'IN_STOCK','Tokyo','LOT-A3',TIMESTAMP '2025-10-10 12:00:00+00'),
('P005','W2',80,15,40,10,'IN_STOCK','Osaka','LOT-B2',TIMESTAMP '2025-10-10 12:00:00+00'),
('P006','W1',22,10,25,50,'LOW','Tokyo','LOT-A4',TIMESTAMP '2025-10-10 12:00:00+00'),
('P007','W2',9,5,20,30,'LOW','Osaka','LOT-B3',TIMESTAMP '2025-10-10 12:00:00+00'),
('P008','W1',60,10,30,0,'IN_STOCK','Tokyo','LOT-A5',TIMESTAMP '2025-10-10 12:00:00+00'),
('P009','W2',110,20,50,0,'IN_STOCK','Osaka','LOT-B4',TIMESTAMP '2025-10-10 12:00:00+00'),
('P010','W1',7,5,20,25,'LOW','Tokyo','LOT-A6',TIMESTAMP '2025-10-10 12:00:00+00');

-- sales: 10件（5オーダー×2明細）
INSERT INTO `mydataset.sales` (
  order_id, order_item_id, order_date, customer_id, product_id, quantity, unit_price, discount, tax_amount, total_amount, currency, status
) VALUES
('O1001','O1001-1',TIMESTAMP '2025-10-11 01:10:00+00','C001','P001',2,19.99,0,2.00,41.98,'JPY','PAID'),
('O1001','O1001-2',TIMESTAMP '2025-10-11 01:10:00+00','C001','P004',1,9.99,0,1.00,10.99,'JPY','PAID'),
('O1002','O1002-1',TIMESTAMP '2025-10-11 03:25:00+00','C002','P003',1,89.50,5.00,8.45,92.95,'JPY','PAID'),
('O1002','O1002-2',TIMESTAMP '2025-10-11 03:25:00+00','C002','P005',2,14.20,0,2.84,30.24,'JPY','PAID'),
('O1003','O1003-1',TIMESTAMP '2025-10-11 05:40:00+00','C003','P007',1,129.00,10.00,11.90,130.90,'JPY','PAID'),
('O1003','O1003-2',TIMESTAMP '2025-10-11 05:40:00+00','C003','P002',1,59.00,0,5.90,64.90,'JPY','PAID'),
('O1004','O1004-1',TIMESTAMP '2025-10-12 02:05:00+00','C004','P008',1,79.90,0,7.99,87.89,'JPY','SHIPPED'),
('O1004','O1004-2',TIMESTAMP '2025-10-12 02:05:00+00','C004','P009',1,24.00,0,2.40,26.40,'JPY','SHIPPED'),
('O1005','O1005-1',TIMESTAMP '2025-10-12 08:55:00+00','C005','P006',1,39.80,0,3.98,43.78,'JPY','PENDING'),
('O1005','O1005-2',TIMESTAMP '2025-10-12 08:55:00+00','C005','P001',1,19.99,0,2.00,21.99,'JPY','PENDING');
