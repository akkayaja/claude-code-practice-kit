-- 연체 표시 시험: '회의를 줄이는 기술'을 11월 1일에 빌린 것처럼 날짜를 앞당겨요
-- (반납 예정일 11월 15일 → 11월 20일 기준 5일 연체)
update public.rentals
   set rented_at = '2026-11-01 10:00:00+09',
       due_date  = '2026-11-15'
 where returned_at is null
   and book_id = (select id from public.books where title = '회의를 줄이는 기술');
