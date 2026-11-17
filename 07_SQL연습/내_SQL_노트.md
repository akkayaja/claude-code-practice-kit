# 내 SQL 노트

> 07 SQL연습(`shop.db`: 고객 200 · 상품 12 · 주문 1,500)에서 쓴 문법 정리

## 1. 쓰는 순서 (이 순서를 꼭 지킨다)

```sql
WITH 임시표 AS (...)        -- (필요할 때만) 중간 결과에 이름 붙이기
SELECT   보여 줄 칸
FROM     어느 표에서
JOIN     다른 표 ON 연결 조건
WHERE    줄 거르기 (묶기 전)
GROUP BY 묶을 기준
ORDER BY 정렬 기준 [DESC]
LIMIT    몇 줄만;
```

## 2. 기초 — 꺼내고, 거르고, 정렬하기

| 문법 | 뜻 | 엑셀로 치면 | 예시 |
|---|---|---|---|
| `SELECT * FROM 표` | 표 전체 보기 | 시트 열기 | `SELECT * FROM customers LIMIT 10;` |
| `SELECT 칸1, 칸2` | 원하는 칸만 | 열 숨기기 | `SELECT name, region FROM customers;` |
| `WHERE 조건` | 조건에 맞는 줄만 | 필터 | `WHERE grade = 'VIP'` |
| `ORDER BY 칸 DESC` | 큰 것부터 정렬 | 내림차순 정렬 | `ORDER BY price DESC` |
| `LIMIT n` | 앞 n줄만 | — | `LIMIT 10` |
| `COUNT(*)` | 줄 수 세기 | COUNTA | `SELECT COUNT(*) FROM orders WHERE status = '취소';` → 135 |

- 글자 값은 **작은따옴표**: `'VIP'`, `'서울'`
- 숫자 비교: `=`, `>=`, `<`, `<>`(같지 않음)
- 조건 여러 개: `AND`(둘 다), `OR`(둘 중 하나)
- `LIKE '2025%'` = "2025로 시작하는"

## 3. 집계 — 묶어서 계산하기

| 문법 | 뜻 | 엑셀로 치면 |
|---|---|---|
| `GROUP BY 칸` | 같은 값끼리 묶기 | 피벗테이블의 '행' |
| `SUM(칸)` / `AVG(칸)` / `COUNT(*)` | 묶음마다 합계 / 평균 / 개수 | 피벗테이블의 '값' |
| `ROUND(값, 1)` | 소수점 자리 맞추기 | ROUND |
| `AS 이름` | 결과 칸에 이름표 붙이기 | 머리글 바꾸기 |

```sql
-- 지역별 고객 수 (6번)
SELECT region, COUNT(*) AS 고객수
FROM customers
GROUP BY region
ORDER BY 고객수 DESC;
```

## 4. JOIN — 번호로 표 이어 붙이기

주문표에는 **번호**(`customer_id`, `product_id`)만 있다 → 번호가 같은 줄끼리 붙여서 이름·가격을 가져온다. (엑셀 VLOOKUP)

```sql
SELECT c.name, p.name, o.qty
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
JOIN products  AS p ON o.product_id  = p.id;
```

- `AS o` = 표 별명 (긴 이름 대신 `o.qty`처럼 짧게)
- 금액 = `o.qty * p.price` → 두 표를 붙여야 계산할 수 있다
- `JOIN` = 짝이 있는 줄만 / `LEFT JOIN` = 짝이 없어도 왼쪽 줄은 남김(빈칸 = `NULL`)

```sql
-- 한 번도 주문 안 한 고객 찾기 (13번) → 0명
SELECT COUNT(*) FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

## 5. 실전 도구

| 문법 | 뜻 | 쓴 곳 |
|---|---|---|
| `substr(글자, 1, 7)` | 글자 앞 7자 자르기 → `2025-11` | 11번 월별 매출 |
| `CASE WHEN 조건 THEN 1 ELSE 0 END` | 조건이면 1, 아니면 0 (엑셀 IF) | 14번 반품 개수 세기 |
| `100.0 * 부분 / 전체` | 비율(%) — `100.0`처럼 소수점을 붙여야 나눗셈이 정확 | 14번 반품률 |
| `WITH 이름 AS (...)` | 중간 결과를 임시 시트처럼 저장 | 15번 |
| `RANK() OVER (PARTITION BY 지역 ORDER BY 수량 DESC)` | 지역마다 따로 순위 | 15번 지역별 1등 |

## 6. 실행 방법

```bash
sqlite3 shop.db < 파일이름.sql
```
- `.headers on` / `.mode column` = 결과를 칸 맞춘 표로 보기

## 7. 해석할 때 조심할 점 (오늘 배운 것)

- **합계는 사람 수에 끌려간다** — VIP 총구매액이 꼴찌(20,245,000원)였지만 VIP는 25명뿐. 비교하려면 1인당 평균도 보기.
- **자주 사는 고객 ≠ 많이 쓰는 고객** — 매출 1등 윤준서 12회 / 구매 횟수 1등 임지우 16회.
- **이름은 겹칠 수 있다** — VIP 중 '최지호'가 2명. 사람은 `id`로 구분한다.
- **"완료" 주문만 셀지 먼저 정하기** — 취소 135건 · 반품 138건이 섞이면 매출이 부풀려진다.
