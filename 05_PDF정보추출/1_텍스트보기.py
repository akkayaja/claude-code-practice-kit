# 1_텍스트보기.py
# PDF 한 장을 열어서, 안에 적힌 글자를 그대로 화면에 출력해 보는 연습용 코드예요.

import pdfplumber  # PDF에서 글자를 뽑아 주는 공구

# 읽을 PDF 파일 위치 (invoices 폴더 안의 1번 거래명세서)
pdf_path = "invoices/거래명세서_01.pdf"

# PDF를 연다 (with를 쓰면 다 읽은 뒤 알아서 닫아 줘요)
with pdfplumber.open(pdf_path) as pdf:
    print(f"📄 파일: {pdf_path}")
    print(f"📑 페이지 수: {len(pdf.pages)}장")
    print("-" * 40)

    # 첫 번째 페이지(pages[0])에서 글자만 뽑는다
    text = pdf.pages[0].extract_text()
    print(text)
