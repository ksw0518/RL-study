import math
import pygame

from physics import BodyControl, BodyProperty, PlanetProperty, run_next_step, landing_status


def main():
    state = {"touched": False, "impact_speed": 0.0, "rest_steps": 0}
    status = "flying"
    
    
    pygame.init()
    w, h = 800, 600
    screen = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 15)

    cx, cy = w / 2.0, h / 2.0 - 200  # 고정 원점 (0, 0)
    body = BodyProperty()
    control = BodyControl()
    planet = PlanetProperty()

    trail = []

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                body = BodyProperty() 
                state = {"touched": False, "impact_speed": 0.0, "rest_steps": 0}
                status = "flying"
                trail.clear()

        keys = pygame.key.get_pressed()
        control.thrust_f = 250.0 if keys[pygame.K_w] else (-250 if keys[pygame.K_s] else 0.0)
        control.thrust_dir = (-5.0 if keys[pygame.K_a] else 0.0) + (5.0 if keys[pygame.K_d] else 0.0)

        run_next_step(body, control, planet, dt)
        status = landing_status(body, planet, state)
        trail.append((cx + body.loc_x, cy - body.loc_y))
        trail = trail[-200:]

        screen.fill((18, 22, 28))
        if len(trail) > 1:
            pygame.draw.lines(screen, (60, 110, 150), False, trail, 2)

        sx, sy = cx + body.loc_x, cy - body.loc_y
        s, c = math.sin(body.dir_head), math.cos(body.dir_head)
        pts = [
            (sx + s * 16, sy - c * 16),
            (sx - c * 10 - s * 10, sy - s * 10 + c * 10),
            (sx + c * 10 - s * 10, sy + s * 10 + c * 10),
        ]
        pygame.draw.polygon(screen, (90, 200, 250), pts)
        pygame.draw.line(screen, (80, 230, 150), (sx, sy), (sx + body.vel_x * 6, sy - body.vel_y * 6), 2)
        pygame.draw.circle(screen, (255, 255, 255), (cx + planet.loc_x, cy - planet.loc_y), planet.radius)

        txt = font.render(
            f"loc=({body.loc_x:.1f}, {body.loc_y:.1f}) head={body.dir_head:.2f} vel=({body.vel_x:.2f}, {body.vel_y:.2f})",
            True,
            (230, 235, 240),
        )
        txt2 = font.render(
        f"status={status} rest={state['rest_steps']} impact={state['impact_speed']:.1f}",
        True, (255, 220, 120))
        screen.blit(txt2, (10, 30))
        screen.blit(txt, (10, 10))
        
        if(status == "crashed") : break
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()