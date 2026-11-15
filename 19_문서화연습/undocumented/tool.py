import csv, sys, os
from collections import defaultdict

def f(a, b=None):
    r = defaultdict(lambda: [0, 0])
    with open(a, encoding="utf-8-sig") as x:
        for row in csv.DictReader(x):
            if b and row["채널"] != b:
                continue
            k = row["날짜"][:7]
            r[k][0] += int(row["매출액"]); r[k][1] += int(row["주문수"])
    return r

def g(r, o):
    with open(o, "w", encoding="utf-8-sig", newline="") as x:
        w = csv.writer(x); w.writerow(["월", "매출", "주문", "객단가"])
        for k in sorted(r):
            s, n = r[k]; w.writerow([k, s, n, round(s / n) if n else 0])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("?"); sys.exit(1)
    g(f(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else None), sys.argv[2])
    print("ok", os.path.abspath(sys.argv[2]))
