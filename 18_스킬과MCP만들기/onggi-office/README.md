# onggi-office 플러그인 (온기마켓 사무실 도구 상자)

클로드코드 실습키트 18번에서 만든 스킬 2개와 MCP 서버 1개를 한 상자에 담았어요.

| 들어 있는 것 | 종류 | 하는 일 |
|---|---|---|
| `weekly-report` | 스킬 (업무 매뉴얼) | "주간보고 써 줘" → 02번 `report.py`로 주간보고 생성 |
| `review-reply` | 스킬 (업무 매뉴얼) | "이 리뷰 답글 달아 줘" → 15번 템플릿 v4 기준 감정·답글·내부조치·긴급도 |
| `shop-db` | MCP 서버 (손 3개) | 07번 `shop.db` **읽기 전용** 조회: 월 매출, 고객 검색, SELECT 자유 조회 |

## 설치 (동료용)

준비물: Claude Code, [uv](https://docs.astral.sh/uv/) (MCP 서버가 `uv`로 `mcp` 공구 상자를 알아서 받아 써요)

이 실습키트 저장소를 내려받은 폴더에서 Claude Code를 열고:

```
/plugin marketplace add akkayaja/claude-code-practice-kit
/plugin install onggi-office@practice-kit
```

터미널에서 하려면:

```bash
claude plugin marketplace add akkayaja/claude-code-practice-kit
claude plugin install onggi-office@practice-kit
```

설치한 뒤 **새 대화**를 열어야 스킬과 손이 보여요.

## 알아 둘 것
- 스킬은 이 저장소의 `02_보고서자동생성/`, `15_프롬프트템플릿/` 파일을 써요. 그래서 **실습키트 폴더에서** 써야 해요.
- `shop-db`는 `./07_SQL연습/shop.db`를 찾아요. 다른 DB를 쓰려면 환경변수 `SHOP_DB`에 경로를 적어요.
- `shop-db`는 DB를 읽기만 해요 (문지기 + 읽기 전용 열기 + query_only, 자물쇠 3개).
- 이 상자 안의 `skills/`와 `server/`는 `4_패키징.py`가 원본에서 복사해 넣은 것이에요. 고칠 때는 원본을 고치고 다시 포장해요.
  - 원본: `.claude/skills/weekly-report`, `.claude/skills/review-reply`, `18_스킬과MCP만들기/1_shop서버.py`
