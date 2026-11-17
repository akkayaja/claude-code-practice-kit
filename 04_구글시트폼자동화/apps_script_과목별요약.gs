/**
 * 04 실습: '과목별 요약' 시트 자동 만들기 + 정원 초과 '대기' 표시
 * 사용법: Apps Script 편집기에 붙여 넣고, 위쪽에서 makeSubjectSummary 를 골라 ▶ 실행
 * (트리거가 이 함수를 부르므로, 대기 표시도 자동으로 같이 돼요)
 */

const CAPACITY = 15; // 과목당 정원

function makeSubjectSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1) 신청 응답이 들어 있는 시트 찾기 (A1 칸이 '타임스탬프'인 시트)
  const source = ss.getSheets().find(s => s.getRange('A1').getValue() === '타임스탬프');
  if (!source) {
    throw new Error("A1 칸이 '타임스탬프'인 시트를 찾지 못했어요. CSV를 제대로 가져왔는지 확인해 주세요.");
  }

  // 2) 표 전체 읽기 → 첫 줄은 제목, 나머지는 신청서
  const values = source.getDataRange().getValues();
  const header = values[0];
  const col = name => header.indexOf(name);
  const NAME = col('이름');
  const SUBJECT = col('신청과목');
  const SCHEDULE = col('희망일정');
  const AGREE = col('개인정보동의');

  const rows = values.slice(1).filter(r => r[NAME] !== '');

  // 3) [도전] 정원 초과 '대기' 표시 → 응답 시트의 '상태' 칸에 적기
  const statuses = markWaitlist(source, values, header);

  // 3-2) [도전] 새 신청자에게 확인 메일 보내기 (테스트 모드: 내 메일로만!)
  const mailCount = sendConfirmationMails(source);

  // 3-3) [도전] 문의사항이 있는 행을 노란색으로 칠하기 (새로 생긴 칸까지 칠하려고 표를 다시 읽어요)
  const fresh = source.getDataRange().getValues();
  const inquiryCount = highlightInquiries(source, fresh, fresh[0]);

  // 4) 세기 (바를 정 자 긋는 계수기)
  const count = (list, idx) => {
    const result = {};
    list.forEach(r => {
      const key = String(r[idx]).trim();
      result[key] = (result[key] || 0) + 1;
    });
    return result;
  };
  const agreedRows = rows.filter(r => String(r[AGREE]).trim() === '네');

  const bySubject = count(rows, SUBJECT);
  const bySubjectAgreed = count(agreedRows, SUBJECT);
  const bySchedule = count(rows, SCHEDULE);

  // 과목별 확정·대기 인원
  const confirmed = {};
  const waiting = {};
  statuses.forEach(s => {
    if (s.status === '확정') confirmed[s.subject] = (confirmed[s.subject] || 0) + 1;
    if (s.status === '대기') waiting[s.subject] = (waiting[s.subject] || 0) + 1;
  });

  // 5) '과목별 요약' 시트 준비 (이미 있으면 비우고 다시 쓰기)
  let summary = ss.getSheetByName('과목별 요약');
  if (summary) {
    summary.clear();
  } else {
    summary = ss.insertSheet('과목별 요약');
  }

  // 6) 표 만들기
  const W = 6; // 표 너비(칸 수)
  const blank = n => Array(n).fill('');
  const output = [];
  output.push(['과목', '전체 신청', '개인정보 동의', '미동의', '확정(정원 ' + CAPACITY + ')', '대기']);
  Object.keys(bySubject).sort((a, b) => bySubject[b] - bySubject[a]).forEach(subject => {
    const all = bySubject[subject];
    const agreed = bySubjectAgreed[subject] || 0;
    output.push([subject, all, agreed, all - agreed, confirmed[subject] || 0, waiting[subject] || 0]);
  });
  const sum = obj => Object.values(obj).reduce((a, b) => a + b, 0);
  output.push(['합계', rows.length, agreedRows.length, rows.length - agreedRows.length, sum(confirmed), sum(waiting)]);
  output.push(blank(W));
  output.push(['일정', '전체 신청'].concat(blank(W - 2)));
  Object.keys(bySchedule).sort().forEach(schedule => {
    output.push([schedule, bySchedule[schedule]].concat(blank(W - 2)));
  });
  output.push(['합계', rows.length].concat(blank(W - 2)));

  summary.getRange(1, 1, output.length, W).setValues(output);

  // 7) 보기 좋게 꾸미기
  const scheduleHeaderRow = Object.keys(bySubject).length + 4;
  [1, scheduleHeaderRow].forEach(r => {
    summary.getRange(r, 1, 1, W).setFontWeight('bold').setBackground('#d9ead3');
  });
  output.forEach((line, i) => {
    if (line[0] === '합계') summary.getRange(i + 1, 1, 1, W).setFontWeight('bold');
  });
  summary.setColumnWidth(1, 160);
  summary.setColumnWidths(2, W - 1, 100);
  summary.getRange(1, W + 2).setValue('마지막 갱신: ' + Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm'));

  summary.getRange(2, W + 2).setValue('문의사항 있는 신청: ' + inquiryCount + '건 (응답 시트에 노란색)');

  Logger.log('완료! 전체 ' + rows.length + '건, 동의 ' + agreedRows.length + '건, 대기 ' + sum(waiting) + '건, 문의 ' + inquiryCount + '건, 메일 ' + mailCount + '통');
}

/**
 * 문의사항이 있는 행을 노란색으로 칠하기
 * - 먼저 모든 행의 배경색을 지우고(새 도화지), 문의가 있는 행만 노란색으로 칠해요
 * - 그래서 문의 내용을 지우면 다음 실행 때 노란색도 자동으로 사라져요
 */
function highlightInquiries(source, values, header) {
  const NAME = header.indexOf('이름');
  const INQUIRY = header.indexOf('문의사항');
  const lastCol = Math.max(header.length, header.indexOf('상태') + 1, INQUIRY + 2);
  const dataRows = values.length - 1;
  if (dataRows < 1) return 0;

  const backgrounds = values.slice(1).map(r => {
    const hasInquiry = r[NAME] !== '' && String(r[INQUIRY]).trim() !== '';
    return Array(lastCol).fill(hasInquiry ? '#fff2cc' : null);
  });
  source.getRange(2, 1, dataRows, lastCol).setBackgrounds(backgrounds);

  return backgrounds.filter(b => b[0] !== null).length;
}

/**
 * 정원 초과 '대기' 표시
 * - 신청 순서(위에서 아래로)대로 줄을 세워요 (선착순)
 * - 개인정보 미동의자는 연락할 수 없으니 '제외(미동의)'
 * - 동의한 사람 중 과목별로 앞에서 15명까지 '확정', 그 뒤는 '대기'
 */
function markWaitlist(source, values, header) {
  const NAME = header.indexOf('이름');
  const SUBJECT = header.indexOf('신청과목');
  const AGREE = header.indexOf('개인정보동의');

  // '상태' 칸이 없으면 맨 오른쪽에 새로 만들기
  let statusCol = header.indexOf('상태');
  if (statusCol === -1) {
    statusCol = header.length;
    source.getRange(1, statusCol + 1).setValue('상태').setFontWeight('bold');
  }

  const seats = {}; // 과목별로 지금까지 '확정'된 인원
  const results = [];
  const statusValues = values.slice(1).map(r => {
    if (r[NAME] === '') return [''];
    const subject = String(r[SUBJECT]).trim();
    let status;
    if (String(r[AGREE]).trim() !== '네') {
      status = '제외(미동의)';
    } else {
      seats[subject] = (seats[subject] || 0) + 1;
      status = seats[subject] <= CAPACITY ? '확정' : '대기';
    }
    results.push({ subject: subject, status: status });
    return [status];
  });

  if (statusValues.length > 0) {
    const range = source.getRange(2, statusCol + 1, statusValues.length, 1);
    range.setValues(statusValues);
    // '대기'는 빨간 글씨로 눈에 띄게
    range.setFontColor(null).setFontWeight('normal');
    statusValues.forEach((v, i) => {
      if (v[0] === '대기') source.getRange(i + 2, statusCol + 1).setFontColor('#cc0000').setFontWeight('bold');
    });
  }
  return results;
}

/**
 * 새 신청자에게 확인 메일 보내기
 * 🔒 안전장치
 *  - 신청자 주소(example.com, 가짜)로는 절대 보내지 않고, '내 메일'로만 보내요
 *  - 처음 실행할 때는 기존 60건에 '기존 신청(발송 안 함)'만 적고 메일은 0통 보내요
 *  - 한 번 실행에 최대 MAX_MAILS_PER_RUN 통까지만 보내요 (실수로 폭탄 메일 방지)
 *  - 이름·과목·일정·동의 칸이 모두 채워진 줄만 보내요 (입력 중인 줄은 건너뜀)
 */
const MAX_MAILS_PER_RUN = 3;

function sendConfirmationMails(source) {
  const myEmail = Session.getEffectiveUser().getEmail(); // 이 스크립트 주인 = 내 메일
  const values = source.getDataRange().getValues();
  const header = values[0];
  const NAME = header.indexOf('이름');
  const EMAIL = header.indexOf('이메일');
  const SUBJECT = header.indexOf('신청과목');
  const SCHEDULE = header.indexOf('희망일정');
  const AGREE = header.indexOf('개인정보동의');
  const STATUS = header.indexOf('상태');

  // '메일발송' 칸 찾기. 없으면 새로 만들고, 지금 있는 줄은 전부 '기존'으로 표시만 하고 끝
  let mailCol = header.indexOf('메일발송');
  if (mailCol === -1) {
    mailCol = header.length;
    source.getRange(1, mailCol + 1).setValue('메일발송').setFontWeight('bold');
    const marks = values.slice(1).map(r => [r[NAME] !== '' ? '기존 신청(발송 안 함)' : '']);
    if (marks.length > 0) source.getRange(2, mailCol + 1, marks.length, 1).setValues(marks);
    return 0;
  }

  let sent = 0;
  for (let i = 1; i < values.length; i++) {
    const r = values[i];
    if (String(r[mailCol]).trim() !== '') continue; // 이미 처리한 줄
    const filled = [NAME, SUBJECT, SCHEDULE, AGREE].every(c => String(r[c]).trim() !== '');
    if (!filled) continue; // 아직 입력 중인 줄
    const cell = source.getRange(i + 1, mailCol + 1);

    if (String(r[AGREE]).trim() !== '네') {
      cell.setValue('발송 안 함(미동의)');
      continue;
    }
    if (sent >= MAX_MAILS_PER_RUN) break;

    const status = STATUS === -1 ? '접수' : String(r[STATUS]).trim();
    const subjectLine = '[특강 신청 확인] ' + r[NAME] + '님, ' + r[SUBJECT] + ' 신청 상태: ' + status;
    const body = [
      '[테스트 메일] 원래 받을 사람: ' + r[EMAIL],
      '',
      r[NAME] + '님, 특강 신청해 주셔서 감사합니다.',
      '',
      '■ 신청 과목: ' + r[SUBJECT],
      '■ 희망 일정: ' + r[SCHEDULE],
      '■ 신청 상태: ' + status + (status === '대기' ? ' (정원 ' + CAPACITY + '명 초과, 자리가 나면 연락드릴게요)' : ''),
      '',
      '감사합니다.'
    ].join('\n');

    MailApp.sendEmail(myEmail, subjectLine, body); // ← 받는 사람은 항상 '나'
    cell.setValue('발송 완료 ' + Utilities.formatDate(new Date(), 'Asia/Seoul', 'MM-dd HH:mm'));
    sent++;
  }
  return sent;
}
