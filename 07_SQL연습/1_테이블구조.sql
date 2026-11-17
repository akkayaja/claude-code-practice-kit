-- 미션 1: shop.db 에 어떤 표(테이블)가 있고, 각 표에 어떤 칸(열)이 있는지 보기

.headers on
.mode column

-- ① 표마다 몇 줄(행)이 들어 있는지 세기
SELECT 'customers(고객)' AS 테이블, COUNT(*) AS 행수 FROM customers
UNION ALL
SELECT 'products(상품)', COUNT(*) FROM products
UNION ALL
SELECT 'orders(주문)', COUNT(*) FROM orders;

-- ② 각 표의 앞 3줄 맛보기
SELECT * FROM customers LIMIT 3;
SELECT * FROM products LIMIT 3;
SELECT * FROM orders LIMIT 3;
