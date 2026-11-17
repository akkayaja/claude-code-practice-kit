-- 미션 3: 문제.md 6~10번 (집계 · JOIN)
-- GROUP BY = 같은 값끼리 묶기 (엑셀 피벗테이블의 '행')
-- SUM / AVG / COUNT = 묶음마다 합계 / 평균 / 개수
-- JOIN ... ON = 번호가 같은 줄끼리 두 표를 옆으로 이어 붙이기 (엑셀 VLOOKUP)
-- AS = 이름표 붙이기 (c = customers, p = products, o = orders 줄임말)

.headers on
.mode column

-- 6번. 지역별 고객 수 (많은 순)
SELECT region, COUNT(*) AS 고객수
FROM customers
GROUP BY region
ORDER BY 고객수 DESC;

-- 7번. 카테고리별 상품 수와 평균 가격
SELECT category, COUNT(*) AS 상품수, ROUND(AVG(price)) AS 평균가격
FROM products
GROUP BY category;

-- 8번. 주문 목록에 고객 이름과 상품 이름을 붙여서 20줄 보기
SELECT o.id AS 주문번호, c.name AS 고객, p.name AS 상품, o.qty, o.status
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
JOIN products  AS p ON o.product_id  = p.id
LIMIT 20;

-- 9번. 상품별 총 판매 수량 (완료 주문만)
SELECT p.name AS 상품, SUM(o.qty) AS 총수량
FROM orders AS o
JOIN products AS p ON o.product_id = p.id
WHERE o.status = '완료'
GROUP BY p.name
ORDER BY 총수량 DESC;

-- 10번. 고객 등급별 총 구매금액 (수량 × 가격, 완료 주문만)
SELECT c.grade AS 등급, SUM(o.qty * p.price) AS 총구매금액
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
JOIN products  AS p ON o.product_id  = p.id
WHERE o.status = '완료'
GROUP BY c.grade
ORDER BY 총구매금액 DESC;
