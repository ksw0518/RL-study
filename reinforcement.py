import math
import numpy as np
from physics import (BodyControl, BodyProperty, PlanetProperty,
                     run_next_step, landing_status)

DT = 1.0 / 60.0  # suppose 60 fps
BODY_R = 12.0
MAIN_THRUST = 250.0
TURN_THRUST = 5.0
MAX_STEPS = 1500
ESCAPE_H = 300.0  # to prevent it from flying away

# random value
SPAWN_ALT = (100.0, 250.0)  # altitude
SPAWN_ANG = 0.5  # radian random range
SPAWN_VEL = 40.0  # start velocity
SPAWN_TILT = 0.5  # start dir

# boundary to form a table
H_BINS    = [5, 20, 50, 100, 200]
VR_BINS   = [-30, -10, -2, 2]
VT_BINS   = [-5, 5]
TILT_BINS = [-0.5, -0.15, 0.15, 0.5]
OM_BINS   = [-0.3, 0.3]
STATE_SHAPE = (6, 5, 3, 5, 3)
N_ACTIONS = 4  # 0 none, 1 main engine, 2 rotate left, 3 rotate right


# what a model can see
def observe(body, planet):
    dx, dy = body.loc_x - planet.loc_x, body.loc_y - planet.loc_y
    dist = math.hypot(dx, dy)
    nx, ny = dx / dist, dy / dist
    h = dist - planet.radius - BODY_R
    vr = body.vel_x * nx + body.vel_y * ny
    vt = body.vel_x * ny - body.vel_y * nx
    up = math.atan2(dx, dy)
    tilt = (body.dir_head - up + math.pi) % (2 * math.pi) - math.pi

    # height from ground, ground direction velocity, sliding velocity, angle, angular velocity
    return h, vr, vt, tilt, body.vel_dir


# discretize to fit the continuous values to a table
def discretize(h, vr, vt, tilt, om):
    return (int(np.digitize(h, H_BINS)),
            int(np.digitize(vr, VR_BINS)),
            int(np.digitize(vt, VT_BINS)),
            int(np.digitize(tilt, TILT_BINS)),
            int(np.digitize(om, OM_BINS)))


# 착륙에 얼마나 근접했는지 예측
# 0에 가까울수록 유리함
def _cost(h, vr, vt, tilt):
    speed = math.hypot(vr, vt)
    return 0.005 * h + 0.01 * speed + 1.0 * abs(tilt)


class LanderEnv:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.planet = PlanetProperty()
        self.control = BodyControl()

    def reset(self):
        p = self.planet
        ang = self.rng.uniform(-SPAWN_ANG, SPAWN_ANG)
        r = p.radius + BODY_R + self.rng.uniform(*SPAWN_ALT)
        b = BodyProperty()
        b.loc_x = p.loc_x + r * math.sin(ang)
        b.loc_y = p.loc_y + r * math.cos(ang)
        b.vel_x = self.rng.uniform(-SPAWN_VEL, SPAWN_VEL)
        b.vel_y = self.rng.uniform(-SPAWN_VEL, SPAWN_VEL)
        b.dir_head = (ang + self.rng.uniform(-SPAWN_TILT, SPAWN_TILT)) % (2 * math.pi)
        self.body = b
        self.state = {"touched": False, "impact_speed": 0.0, "rest_steps": 0}
        self.t = 0
        o = observe(b, p)
        self.prev_cost = _cost(*o[:4])
        return discretize(*o)

    # 현재 상태에서 action 이후 상태 이산화해서 반환
    def step(self, action):
        # action 적용
        c = self.control
        c.thrust_f = MAIN_THRUST if action == 1 else 0.0
        c.thrust_dir = (-TURN_THRUST if action == 2 else
                        TURN_THRUST if action == 3 else 0.0)

        # 물리 진행
        run_next_step(self.body, c, self.planet, DT, body_radius=BODY_R)
        self.t += 1
        status = landing_status(self.body, self.planet, self.state)

        # o = 모델이 보는 환경
        o = observe(self.body, self.planet)

        # 현재 환경 상황에서 cost 계산
        cost = _cost(*o[:4])

        # 상태가 좋아지면 양수
        reward = self.prev_cost - cost
        self.prev_cost = cost

        # 시간 패널티
        reward -= 0.01

        # 연료 사용 페널티
        if action == 1:
            reward -= 0.01
        elif action in (2, 3):
            reward -= 0.001

        done = False
        if status == "landed":
            reward += 200.0; done = True
        elif status == "crashed":
            reward -= 120.0; done = True
        elif o[0] > ESCAPE_H:
            reward -= 100.0; done = True
            status = "escaped"
        elif self.t >= MAX_STEPS:
            reward -= 50.0; done = True
            status = "timeout"

        return discretize(*o), reward, done, {"status": status, "raw": o}