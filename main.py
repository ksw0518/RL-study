import numpy as np, csv
from collections import Counter
from reinforcement import LanderEnv, STATE_SHAPE, N_ACTIONS

EPISODES = 20000
ALPHA, GAMMA = 0.1, 0.99
EPS_START, EPS_END = 1.0, 0.05
EPS_DECAY_EPISODES = 13000   # 이 시점까지 선형 감소

Q = np.zeros(STATE_SHAPE + (N_ACTIONS,))
env = LanderEnv(seed=0)
rng = np.random.default_rng(1)
log = open("q_log.csv", "w", newline="")
w = csv.writer(log); w.writerow(["episode", "reward", "status", "eps"])
recent = Counter()

for ep in range(EPISODES):
    # eps 점진적 감소 -> 초반엔 대부분 랜덤 탐색, 후반에는 조금만 탐색
    eps = max(EPS_END, EPS_START - (EPS_START - EPS_END) * ep / EPS_DECAY_EPISODES)
    
    
    s = env.reset()
    done = False
    total = 0.0
    
    
    while not done:
        if rng.random() < eps:
            # 일정 비율로 랜덤 탐색
            a = int(rng.integers(N_ACTIONS))
        else:
            # q 표 값에 의해 행동 (기록된 보상이 가장 큰 행동 선택)
            q = Q[s]
            a = int(rng.choice(np.flatnonzero(q == q.max())))   # 동률이면 랜덤
        
        # 다음 state 및 행동에 따른 보상 계산
        s2, r, done, info = env.step(a)
        
        # 종단 상태라면 target을 r로 설정
        # 종단 상태가 아니라면 다음 상태에서 취할 수 있는 최댓값 * r을 더함
        target = r if done else r + GAMMA * Q[s2].max()
        
        Q[s + (a,)] += ALPHA * (target - Q[s + (a,)])
        
        s = s2
        total += r
        
    w.writerow([ep, total, info["status"], eps])
    recent[info["status"]] += 1
    if (ep + 1) % 1000 == 0:
        print(ep + 1, dict(recent), f"eps={eps:.2f}")
        recent.clear()

np.save("Q.npy", Q)
log.close()