-- 5단계: 대여 장부(rentals 테이블)와 대여·반납 함수 만들기

-- 1) 대여 장부: "누가, 어떤 책을, 언제 빌렸고, 언제까지 돌려줘야 하고, 언제 돌려줬나"
create table public.rentals (
  id          bigint generated always as identity primary key,
  book_id     bigint not null references public.books(id) on delete cascade, -- 어떤 책 (책이 지워지면 기록도 같이 지워짐)
  user_id     uuid   not null references auth.users(id) on delete cascade default auth.uid(), -- 누가 (로그인한 사람)
  user_email  text,                                       -- 누가 (사람이 읽기 쉬운 이메일)
  rented_at   timestamptz not null default now(),         -- 빌린 시각
  due_date    date not null default (current_date + 14),  -- 반납 예정일 (빌린 날 + 14일)
  returned_at timestamptz                                 -- 반납한 시각 (비어 있으면 아직 대여 중)
);

-- 2) 경비원: 장부는 "내 기록만" 볼 수 있어요.
--    직접 쓰기·고치기는 막고, 아래 두 함수(대여 창구·반납 창구)로만 기록이 바뀌어요.
alter table public.rentals enable row level security;
create policy "내 대여 기록만 보기" on public.rentals
  for select to authenticated using (user_id = auth.uid());

-- 3) 대여 창구: 규칙을 확인하고 통과하면 장부에 적고 책을 '대여 중'으로 바꿔요
create or replace function public.rent_book(p_book_id bigint)
returns void
language plpgsql
security definer          -- 창구 직원 권한으로 실행 (책 상태를 바꿀 수 있게)
set search_path = ''
as $$
declare
  v_user uuid := auth.uid();
  v_available boolean;
  v_count int;
begin
  if v_user is null then
    raise exception '로그인이 필요해요';
  end if;

  -- 책 상태 확인 (동시에 두 사람이 빌리지 못하게 잠깐 잠가요)
  select available into v_available from public.books where id = p_book_id for update;
  if v_available is null then
    raise exception '없는 책이에요';
  elsif v_available = false then
    raise exception '이미 대여 중인 책이에요';
  end if;

  -- 규칙: 한 사람은 동시에 최대 3권
  select count(*) into v_count from public.rentals
   where user_id = v_user and returned_at is null;
  if v_count >= 3 then
    raise exception '한 사람은 최대 3권까지 빌릴 수 있어요 (지금 %권 대여 중)', v_count;
  end if;

  insert into public.rentals (book_id, user_id, user_email)
  values (p_book_id, v_user, auth.jwt() ->> 'email');

  update public.books set available = false where id = p_book_id;
end;
$$;

-- 4) 반납 창구: 내가 빌린 책인지 확인하고, 반납 시각을 적고 책을 '가능'으로 돌려놔요
create or replace function public.return_book(p_rental_id bigint)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_book bigint;
begin
  select book_id into v_book from public.rentals
   where id = p_rental_id and user_id = auth.uid() and returned_at is null
   for update;
  if v_book is null then
    raise exception '내가 대여 중인 기록이 아니에요';
  end if;

  update public.rentals set returned_at = now() where id = p_rental_id;
  update public.books set available = true where id = v_book;
end;
$$;

-- 5) 창구 이용 권한: 로그인한 사람만
revoke execute on function public.rent_book(bigint)   from public, anon;
revoke execute on function public.return_book(bigint) from public, anon;
grant  execute on function public.rent_book(bigint)   to authenticated;
grant  execute on function public.return_book(bigint) to authenticated;
