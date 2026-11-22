# 스킬과 MCP 사용법 (18번 실습 결과물)

> 한 줄 요약: **스킬 = AI에게 주는 업무 매뉴얼**, **MCP = AI에게 달아 주는 새 손**

## 1. 한눈에 비교

| | 스킬 (Skill) | MCP 서버 |
|---|---|---|
| 비유 | 업무 매뉴얼 | 새 손 (도구) |
| 정하는 것 | **어떻게** 일할지 (순서·양식·규칙) | **무엇을** 만질 수 있는지 (DB, 외부 서비스) |
| 생김새 | 글 파일 `SKILL.md` | 계속 켜져 있는 프로그램 (`1_shop서버.py`) |
| 언제 쓰이나 | 요청이 매뉴얼의 `description`과 맞으면 Claude가 꺼내 읽음 | Claude가 필요하다고 판단하면 손을 빌려 씀 |
| 만든 것 | `.claude/skills/weekly-report/`, `.claude/skills/review-reply/` | `18_스킬과MCP만들기/1_shop서버.py` + `.mcp.json` |

둘은 함께 쓸 수 있어요. 예: "월간 매출 보고서 써 줘" 스킬(순서·양식) 안에서 `shop-db` 손(데이터 조회)을 쓰게 하기.

## 2. 스킬: 주간보고-작성 (`weekly-report`)

- **위치:** 실습키트 `.claude/skills/weekly-report/SKILL.md`
- **이렇게 말하면 쓰여요:** "주간보고 써 줘", "3주차 보고서 만들어 줘"
- **하는 일:** 02번 `report.py` 실행 → 숫자 확인 → 정해진 양식으로 요약
- **원칙:** 숫자 계산은 코드가 한다 (Claude는 옮기고 확인만)
- **결과:** `02_보고서자동생성/결과/주간보고_11월(_N주차).md`, `.docx` (실행할 때마다 덮어씀)
- **고치려면:** `SKILL.md`를 고치고 **새 대화**에서 다시 요청 (매뉴얼 목록은 대화 시작할 때 읽어요)

## 3. MCP: shop-db (07번 shop.db 조회)

### 손 3개
| 손 이름 | 하는 일 | 기준 |
|---|---|---|
| `sales_by_month` | 한 달 매출 (`month`: `YYYY-MM`, 비우면 지난달) | **완료 주문만**, 매출 = 수량 × 가격 |
| `search_customers` | 고객 검색 (`keyword`: 이름 일부·지역·등급) | 최대 20명, 구매액은 완료 주문만 |
| `run_select` (도전) | SELECT 문으로 자유 조회 | 최대 50줄, **읽기 전용** |

### 🔒 읽기 전용 안전장치 (자물쇠 3개)
| 자물쇠 | 하는 일 |
|---|---|
| ① 문지기 | `SELECT`/`WITH`로 시작하는 문장 하나만 들여보냄 (`;`로 이어 붙이기 금지) |
| ② `mode=ro` | DB 파일을 보기 전용으로 열기 → 문지기를 속여도 못 고침 |
| ③ `query_only` | 연결 자체를 한 번 더 잠금 |

시험: `cd 18_스킬과MCP만들기 && .venv/bin/python 3_안전장치시험.py` → 나쁜 명령 5개 모두 거절, shop.db 지문 그대로

### 이렇게 물어보세요
- "지난달 매출 알려 줘" → 2026-10: **7,414,500원**, 완료 46건
- "2026년 5월 매출 알려 줘"
- "민준이라는 고객 찾아 줘" → 11명
- "서울 VIP 고객 보여 줘"

### 설치(등록)·삭제
실습키트 맨 위 폴더에서:
```bash
# 0) 18 폴더에 작업실 만들기 (처음 한 번)
cd 18_스킬과MCP만들기 && uv venv --python 3.12 && uv pip install mcp && cd ..
# 1) 손 등록 → .mcp.json 이 생김
claude mcp add shop-db --scope project -- 18_스킬과MCP만들기/.venv/bin/python 18_스킬과MCP만들기/1_shop서버.py
# 확인
claude mcp list
# 삭제
claude mcp remove shop-db --scope project
```

### 시험하기 (Claude 없이)
```bash
cd 18_스킬과MCP만들기 && .venv/bin/python 2_서버시험.py
```
손 3개 목록 + 지난달 매출 + '민준' 고객 검색 결과가 나와요.

## 4. 스킬: 리뷰-답글 (`review-reply`) — 도전

- **위치:** 실습키트 `.claude/skills/review-reply/SKILL.md`
- **기준:** 15번 `템플릿_v4.txt`를 그대로 읽어요 (기준은 템플릿 한 곳에만)
- **갈래 ① 바로 답하기:** "이 리뷰 답글 달아 줘: …" → 리뷰마다 감정/답글/내부조치/긴급도 4줄 + 판단 근거 (API 비용 없음)
- **갈래 ② 전체 처리:** "리뷰 전체 처리해 줘" → 15번 `3_전체처리.py 템플릿_v4.txt` → `결과/리뷰_답글_v4.csv`

## 5. 선물 상자: onggi-office 플러그인 — 도전

- 스킬 2개 + `shop-db` 손을 상자 `18_스킬과MCP만들기/onggi-office/`에 담았어요. 진열대 목록은 맨 위 `.claude-plugin/marketplace.json`.
- 원본을 고친 뒤 다시 포장: `cd 18_스킬과MCP만들기 && python3 4_패키징.py` (복사 + 검사)
- 동료 설치 방법은 `onggi-office/README.md`:
  `claude plugin marketplace add akkayaja/claude-code-practice-kit` → `claude plugin install onggi-office@practice-kit`

## 6. 막혔을 때
| 증상 | 해결 |
|---|---|
| 스킬·손이 안 보여요 | **새 대화**를 여세요 (대화 시작할 때만 목록을 읽어요) |
| 새 대화에서 `shop-db`가 없어요 | 대화 폴더가 **실습키트 폴더 자체**인지 확인 (worktree 안이면 `.mcp.json`이 안 보여요) |
| "써도 될까요?" 창이 떠요 | 처음 한 번 묻는 안전 확인이에요. 허용을 누르세요 |
| 서버 코드를 고쳤는데 그대로예요 | 서버는 켤 때 코드를 한 번만 읽어요. 새 대화를 여세요 |
| 서버 코드에 `print()`를 넣었더니 고장 | stdio 서버는 화면 출력이 곧 대화 통로라서 `print()`를 쓰면 안 돼요 |
