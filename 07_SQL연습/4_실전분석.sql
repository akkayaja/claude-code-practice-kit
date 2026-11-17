-- 미션 4: 문제.md 11~15번 (실전 분석)
-- substr(글자, 시작, 길이) = 글자 일부 잘라내기 ('2025-11-14 10:10' → '2025-11')
-- LEFT JOIN = 짝이 없어도 왼쪽 표의 줄은 남기기 (짝 없는 칸은 NULL = 빈칸)
-- CASE WHEN ... THEN 1 ELSE 0 END = 조건에 맞으면 1, 아니면 0 (엑셀 IF)
-- WITH 이름 AS (...) = 중간 결과에 이름 붙여 두기 (엑셀의 '임시 시트')
-- RANK() OVER (PARTITION BY 지역 ...) = 지역마다 따로 1등, 2등 … 순위 매기기

.headers on
.mode column

-- 11번. 2025년 월별 매출 추이 (완료 주문만)
SELECT substr(o.ordered_at, 1, 7) AS 월, SUM(o.qty * p.price) AS 매출
FROM orders AS o
JOIN products AS p ON o.product_id = p.id
WHERE o.status = '완료' AND o.ordered_at LIKE '2025%'
GROUP BY 월
ORDER BY 월;

-- 12번. 매출 TOP 10 고객과 각자의 구매 횟수 (완료 주문만)
SELECT c.name AS 고객, c.grade AS 등급,
       SUM(o.qty * p.price) AS 총구매금액,
       COUNT(*) AS 구매횟수
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
JOIN products  AS p ON o.product_id  = p.id
WHERE o.status = '완료'
GROUP BY c.id
ORDER BY 총구매금액 DESC
LIMIT 10;

-- 13번. 한 번도 주문하지 않은 고객이 있는지
SELECT COUNT(*) AS 주문없는_고객수
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.id IS NULL;

-- 14번. 반품률(반품 ÷ 전체 주문)이 가장 높은 상품 (상위 3개)
SELECT p.name AS 상품,
       COUNT(*) AS 전체주문,
       SUM(CASE WHEN o.status = '반품' THEN 1 ELSE 0 END) AS 반품,
       ROUND(100.0 * SUM(CASE WHEN o.status = '반품' THEN 1 ELSE 0 END) / COUNT(*), 1) AS 반품률_퍼센트
FROM orders AS o
JOIN products AS p ON o.product_id = p.id
GROUP BY p.id
ORDER BY 반품률_퍼센트 DESC
LIMIT 3;

-- 15번. 지역별로 가장 많이 팔린 상품 1개씩 (완료 주문의 수량 기준)
WITH 지역상품 AS (
    SELECT c.region AS 지역, p.name AS 상품, SUM(o.qty) AS 수량,
           RANK() OVER (PARTITION BY c.region ORDER BY SUM(o.qty) DESC) AS 순위
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.id
    JOIN products  AS p ON o.product_id  = p.id
    WHERE o.status = '완료'
    GROUP BY c.region, p.name
)
SELECT 지역, 상품, 수량
FROM 지역상품
WHERE 순위 = 1
ORDER BY 지역;
