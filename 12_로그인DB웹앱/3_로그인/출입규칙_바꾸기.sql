-- 4단계: 경비원(RLS) 규칙 바꾸기
-- 지금까지는 "누구나" 볼 수 있었는데, 이제 "로그인한 사람만" 볼 수 있게 해요.

-- 1) 3단계에서 만든 임시 규칙 3개 떼어 내기
drop policy "임시: 누구나 보기" on public.books;
drop policy "임시: 누구나 추가" on public.books;
drop policy "임시: 누구나 삭제" on public.books;

-- 2) 새 규칙: to authenticated = "로그인해서 출입증을 받은 사람"에게만
create policy "로그인한 사람: 보기" on public.books for select to authenticated using (true);
create policy "로그인한 사람: 추가" on public.books for insert to authenticated with check (true);
create policy "로그인한 사람: 삭제" on public.books for delete to authenticated using (true);
-- (도전 미션에서 "추가·삭제는 관리자만"으로 한 번 더 좁힐 거예요)
