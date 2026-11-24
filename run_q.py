# run_q.py
# 사용법:
#   python run_q.py                  -> Q.npy로 실행 (무한 반복, ESC로 종료)
#   python run_q.py Q_05000.npy      -> 다른 테이블로 실행
#   python run_q.py --n 10           -> 10번만 실행하고 성공률 출력
import sys
from collections import Counter
import numpy as np
import pygame
from viz import Viewer

qfile = next((a for a in sys.argv[1:] if a.endswith(".npy")), "Q.npy")
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else None

Q = np.load(qfile)
viewer = Viewer()
results = Counter()

ep = 0
while viewer.enabled and (n is None or ep < n):
    # 시드를 바꿔가며 다양한 시작 조건에서 실행
    status = viewer.play(Q, f"{qfile}  run {ep + 1}", seed=1000 + ep, fps=60)
    results[status] += 1
    ep += 1

pygame.quit()
print(dict(results))