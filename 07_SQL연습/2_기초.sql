-- 미션 2: 문제.md 1~5번 (기초)
-- SELECT = 보여 줘 / FROM = 어느 표에서 / WHERE = 이 조건에 맞는 것만
-- ORDER BY = 이 순서로 / LIMIT = 몇 줄만 / COUNT(*) = 몇 줄인지 세기

.headers on
.mode column

-- 1번. 고객 테이블의 모든 데이터를 10줄만 보기
SELECT * FROM customers LIMIT 10;

-- 2번. 등급이 'VIP'인 고객의 이름과 지역
SELECT name, region FROM customers WHERE grade = 'VIP';

-- 3번. 가격이 30,000원 이상인 상품을 비싼 순으로
SELECT name, price FROM products WHERE price >= 30000 ORDER BY price DESC;

-- 4번. 지역이 '서울'인 고객 수
SELECT COUNT(*) AS 서울_고객수 FROM customers WHERE region = '서울';

-- 5번. 상태가 '취소'인 주문 수
SELECT COUNT(*) AS 취소_주문수 FROM orders WHERE status = '취소';
