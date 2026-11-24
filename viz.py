# viz.py
import math
import numpy as np
import pygame
from reinforcement import LanderEnv

W, H = 800, 600
CX, CY = W / 2.0, H / 2.0 - 100     # main.py와 같은 원점


class Viewer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Q-learning lander")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 15)
        self.big = pygame.font.SysFont("consolas", 32)
        self.enabled = True

    def pump(self):
        """학습 중 창이 멈추지 않게 주기적으로 호출. ESC/창 닫기 -> 렌더링만 끔(학습은 계속)."""
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                self.enabled = False
                pygame.display.quit()
                return False
        return True

    def _draw(self, env, trail, action, title, status, t):
        b, p = env.body, env.planet
        scr = self.screen
        scr.fill((18, 22, 28))
        pygame.draw.circle(scr, (255, 255, 255), (CX + p.loc_x, CY - p.loc_y), p.radius)
        if len(trail) > 1:
            pygame.draw.lines(scr, (60, 110, 150), False, trail, 2)

        sx, sy = CX + b.loc_x, CY - b.loc_y
        s, c = math.sin(b.dir_head), math.cos(b.dir_head)
        pts = [(sx + s * 16, sy - c * 16),
               (sx - c * 10 - s * 10, sy - s * 10 + c * 10),
               (sx + c * 10 - s * 10, sy + s * 10 + c * 10)]
        pygame.draw.polygon(scr, (90, 200, 250), pts)
        if action == 1:   # 기체 뒤쪽 불꽃
            flame = [(sx - s * 4 - c * 5, sy + c * 4 - s * 5),
                     (sx - s * 4 + c * 5, sy + c * 4 + s * 5),
                     (sx - s * 22, sy + c * 22)]
            pygame.draw.polygon(scr, (255, 160, 40), flame)

        names = ["coast", "MAIN", "turn L", "turn R"]
        scr.blit(self.font.render(title, True, (255, 220, 120)), (10, 10))
        scr.blit(self.font.render(f"t={t}  action={names[action]}  status={status}",
                                  True, (230, 235, 240)), (10, 30))
        scr.blit(self.font.render("SPACE: skip   ESC: stop rendering",
                                  True, (150, 150, 160)), (10, H - 25))

    def play(self, Q, title, seed=123, fps=120):
        """greedy 정책으로 한 에피소드를 애니메이션. 결과 status 문자열을 반환."""
        if not self.enabled:
            return None
        env = LanderEnv(seed=seed)
        s = env.reset()
        done, t, action, status = False, 0, 0, "flying"
        trail = []
        while not done:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    self.enabled = False
                    pygame.display.quit()
                    return status
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    return status
            action = int(np.argmax(Q[s]))
            s, _, done, info = env.step(action)
            status = info["status"]
            t += 1
            trail.append((CX + env.body.loc_x, CY - env.body.loc_y))
            trail = trail[-200:]
            self._draw(env, trail, action, title, status, t)
            pygame.display.flip()
            self.clock.tick(fps)        # 60 = 실시간, 120 = 2배속

        color = (120, 255, 150) if status == "landed" else (255, 120, 120)
        label = self.big.render(status.upper(), True, color)
        self.screen.blit(label, (W / 2 - label.get_width() / 2, 60))
        pygame.display.flip()
        pygame.time.wait(1200)
        return status