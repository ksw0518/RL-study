import math
import pygame

class PlanetProperty:
    def __init__(self):
                # current location
                self.loc_x: float = 0.0
                self.loc_y: float = -300.0
                self.radius : float = 150.0
                self.grav_const : float = 10000000 / 2

class BodyProperty:
    def __init__(self):
            # current location
            self.loc_x: float = 0.0
            self.loc_y: float = 0.0
            
            # velocity
            self.vel_x: float = 0.0
            self.vel_y: float = 0.0
            
            # radian, rotational speed
            self.vel_dir : float = 0.0
            # dir_head 0 heads upward
            self.dir_head: float = 0.0

class BodyControl:
    def __init__(self):
        # forward thrust
        self.thrust_f: float = 0.0
        
        # rotational thrust (negative - left angular acceleration, positive - right angular acceleration)
        self.thrust_dir : float = 0.0

def detect_collide(m_property: BodyProperty, m_planet: PlanetProperty, body_radius: float = 12.0):
    x_diff = m_property.loc_x - m_planet.loc_x
    y_diff = m_property.loc_y - m_planet.loc_y
    planet_ship_dist_sqr: float = x_diff * x_diff + y_diff * y_diff
    limit_dist = m_planet.radius + body_radius
    return planet_ship_dist_sqr <= limit_dist * limit_dist
    
def run_next_step(m_property : BodyProperty, m_control: BodyControl, m_planet:PlanetProperty, dt : float, 
                  body_radius: float = 12.0, restitution: float = 0.55, tangent_damping: float = 0.96):
    # update direction speed
    m_property.vel_dir += m_control.thrust_dir * dt
    
    # update direction
    m_property.dir_head += m_property.vel_dir * dt
    
    # keeps the range to 0 ~ 2pi
    if(m_property.dir_head > 2 * math.pi):
        m_property.dir_head -= 2 * math.pi
    elif(m_property.dir_head < 0):
        m_property.dir_head += 2 * math.pi
    
   
    
    # update velocity change by engine
    m_property.vel_x += math.sin(m_property.dir_head) * m_control.thrust_f * dt
    m_property.vel_y += math.cos(m_property.dir_head) * m_control.thrust_f * dt
    
    
    
    # gravity pulling
    x_diff = m_property.loc_x - m_planet.loc_x
    y_diff = m_property.loc_y - m_planet.loc_y
    planet_ship_dist_sqr :float = (x_diff) ** 2 + (y_diff) ** 2
    gravity : float = m_planet.grav_const / planet_ship_dist_sqr
    
    dir_x = x_diff / math.sqrt(planet_ship_dist_sqr)
    dir_y = y_diff / math.sqrt(planet_ship_dist_sqr)
    
    grav_x = -gravity * dir_x
    grav_y = -gravity * dir_y
    
    m_property.vel_x += grav_x * dt
    m_property.vel_y += grav_y * dt
    
   

    
    m_property.loc_x += m_property.vel_x * dt
    m_property.loc_y += m_property.vel_y * dt
    
    # detect collision between planet, ship
    # detect and resolve bouncing collision between planet and ship
    if detect_collide(m_property, m_planet, body_radius=body_radius):
        surface_dist = m_planet.radius + body_radius
        m_property.loc_x = m_planet.loc_x + dir_x * surface_dist
        m_property.loc_y = m_planet.loc_y + dir_y * surface_dist

        vn = m_property.vel_x * dir_x + m_property.vel_y * dir_y
        vtx = m_property.vel_x - vn * dir_x
        vty = m_property.vel_y - vn * dir_y

        if vn < 0.0:
            vn = -restitution * vn

        vtx *= tangent_damping
        vty *= tangent_damping

        m_property.vel_x = vtx + vn * dir_x
        m_property.vel_y = vty + vn * dir_y


def landing_status(body, planet, state, body_radius=12.0,
                   v_max=50.0, tilt_max=0.35, rest_v=2.0, rest_steps=60):  
    dx = body.loc_x - planet.loc_x
    dy = body.loc_y - planet.loc_y
    
    # hypot calculates the pythagoras thingy
    dist = math.hypot(dx, dy)

    
    up_angle = math.atan2(dx, dy)
    tilt = abs((body.dir_head - up_angle + math.pi) % (2 * math.pi) - math.pi)

    touching = dist <= planet.radius + body_radius + 0.5
    speed = math.hypot(body.vel_x, body.vel_y)

    if touching:
        if not state["touched"]:
            state["touched"] = True
            state["impact_speed"] = speed
            if speed > v_max:
                return "crashed"
        if speed < rest_v and tilt < tilt_max:
            state["rest_steps"] += 1
            if state["rest_steps"] >= rest_steps:
                return "landed"
        else:
            state["rest_steps"] = 0
    else:
        # resets when not touching
        state["touched"] = False
        state["rest_steps"] = 0
    return "flying"


def main():
    return 0

if __name__ == "__main__":
    main()