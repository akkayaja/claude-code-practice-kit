-- 도전 ②: 관리자는 모든 사람의 대여 기록을 볼 수 있게 하기
-- (직원은 여전히 "내 기록만" 볼 수 있어요. 규칙은 '또는'으로 합쳐져요)
create policy "관리자: 모든 대여 기록 보기" on public.rentals
  for select to authenticated using ((select public.is_admin()));
