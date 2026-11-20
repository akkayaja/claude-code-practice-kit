-- 도전 ①: 관리자만 책을 추가·수정·삭제할 수 있게 하기

-- 1) 관리자 명단 (여기에 이름이 있으면 관리자)
create table public.admins (
  user_id uuid primary key references auth.users(id) on delete cascade
);
alter table public.admins enable row level security;
-- 명단은 앱에서 직접 못 봐요. 아래 is_admin() 함수로 "나 관리자야?"만 물어볼 수 있어요.

-- 2) "지금 로그인한 사람이 관리자인가?"를 알려 주는 함수
create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;
revoke execute on function public.is_admin() from public, anon;
grant  execute on function public.is_admin() to authenticated;

-- 3) 책장 규칙 바꾸기: 보기는 로그인한 사람 누구나, 추가·수정·삭제는 관리자만
drop policy "로그인한 사람: 추가" on public.books;
drop policy "로그인한 사람: 삭제" on public.books;
create policy "관리자만: 추가" on public.books for insert to authenticated with check ((select public.is_admin()));
create policy "관리자만: 수정" on public.books for update to authenticated using ((select public.is_admin())) with check ((select public.is_admin()));
create policy "관리자만: 삭제" on public.books for delete to authenticated using ((select public.is_admin()));

-- 4) 첫 관리자 지정: 지금까지 가입한 첫 번째 계정
insert into public.admins (user_id)
select id from auth.users order by created_at limit 1;
