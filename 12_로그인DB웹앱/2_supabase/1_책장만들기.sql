-- 3단계: Supabase 창고에 책장(books 테이블)을 만들고 책 10권을 넣어요
-- (Supabase 대시보드 > SQL Editor에 붙여 넣어도 똑같이 동작해요)

-- 1) 책장 만들기: 칸(열)마다 이름과 종류를 정해요
create table public.books (
  id         bigint generated always as identity primary key, -- 책 번호 (자동으로 1, 2, 3… 매겨짐)
  title      text not null,                                   -- 제목 (비우면 안 됨)
  author     text not null,                                   -- 저자
  category   text not null,                                   -- 카테고리
  available  boolean not null default true,                   -- 대여 가능 여부 (기본값: 가능)
  created_at timestamptz not null default now()               -- 등록한 시각
);

-- 2) seed/books.json의 책 10권 넣기 (넣는 순서대로 번호 1~10이 붙어요)
insert into public.books (title, author, category, available) values
  ('데이터로 일하는 법',     '김연습', '업무',     true),
  ('파이썬 첫걸음',          '이코딩', 'IT',       false),
  ('엑셀 자동화 입문',       '박엑셀', 'IT',       false),
  ('일 잘하는 사람의 메모',  '최메모', '업무',     true),
  ('마케팅 기초',            '정마케', '경영',     false),
  ('AI와 함께 일하기',       '한에이', 'IT',       false),
  ('회의를 줄이는 기술',     '오회의', '업무',     true),
  ('숫자 읽는 습관',         '서숫자', '경영',     true),
  ('글쓰기의 기본',          '신글쓰', '자기계발', true),
  ('시간 관리 노트',         '권시간', '자기계발', true);

-- 3) 창고 경비원(RLS) 켜기: 규칙에 적힌 일만 허락해요
alter table public.books enable row level security;

-- 4) 임시 규칙: 아직 로그인이 없으니 누구나 보기·추가·삭제 가능
--    (4단계 로그인 때 "로그인한 사람만"으로 바꿀 거예요)
create policy "임시: 누구나 보기"   on public.books for select using (true);
create policy "임시: 누구나 추가"   on public.books for insert with check (true);
create policy "임시: 누구나 삭제"   on public.books for delete using (true);
