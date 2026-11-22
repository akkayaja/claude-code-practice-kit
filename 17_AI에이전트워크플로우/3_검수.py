# 미션 2-③: 편집장 에이전트에게 초안 '검수'를 맡기기 (수동 3단계)
#  2_초안.py 가 남긴 결과/주제1/2_초안.md 를 읽어서 검수기준 6개로 채점해요
import json
from 공통 import 주제_읽기, 주제폴더, 검수하기, 검수표

주제 = 주제_읽기()[0]                       # 주제 1번
폴더 = 주제폴더(주제)
초안 = (폴더 / "2_초안.md").read_text(encoding="utf-8")   # 앞 단계 결과 받기
print(f"📋 주제 {주제['번호']}: {주제['주제']}")
print("③ 편집장이 검수기준 6개로 채점하는 중... (10~30초)\n")

결과 = 검수하기(주제, 초안)
표 = 검수표(결과)
print(표)

(폴더 / "3_검수.md").write_text(표, encoding="utf-8")                      # 사람이 읽을 표
(폴더 / "3_검수.json").write_text(json.dumps(결과, ensure_ascii=False, indent=2), encoding="utf-8")  # 다음 단계(작가)가 읽을 기록
print("\n💾 저장: 결과/주제1/3_검수.md, 결과/주제1/3_검수.json")
