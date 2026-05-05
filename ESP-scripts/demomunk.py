import pymunk
import pymunk.pygame_util
import math
import json
import pygame
import random
import sys
from hashlib import sha256
import pickle
import os

BACKGROUND = (180, 180, 180)
TARGET_FPS = 60
EVAL_STEPS = 500
VIEW_STEPS = TARGET_FPS * 9    # 9 simulated seconds = 540 physics steps

SPEEDS = [0.25, 0.5, 1, 2, 3, 5, 8, 13, 21]
DEFAULT_SPEED_IDX = 2

LEFT_W  = 220
RIGHT_W = 280
HUD_H   = 44

BG_DARK  = (15, 14, 20)
PANEL_BG = (28, 38, 65)
ACCENT   = (80, 220, 140)
ACCENT2  = (40, 160, 100)
DIM      = (130, 140, 165)
WHITE    = (230, 230, 230)

ACT_COLORS = {
    'tanh':    (100, 150, 255),
    'sin':     (200, 100, 255),
    'elu':     (255, 160,  50),
    'gauss':   (255, 120, 180),
    'inv':     (255,  80,  80),
    'sigmoid': ( 80, 200, 120),
}
AGG_COLORS = {
    'min':     (180,  60,  60),
    'max':     ( 60, 200,  80),
    'sum':     ( 80, 130, 220),
    'product': (220, 150,  40),
    'mean':    (150, 150, 170),
}
DEFAULT_ACT_COLOR = (130, 130, 150)
DEFAULT_AGG_COLOR = (80,  80, 100)


# name helpers

def generate_name(s):   # stolen from https://github.com/carykh/jes/blob/main/utils.py
    _hex    = sha256(str(s).encode('utf-8')).hexdigest()
    result  = int(_hex, 16)
    length  = [5, 5, 6, 6, 7][result % 5]
    result //= 5
    letters = ["bcdfghjklmnprstvwxz", "aeiouy"]
    name    = ""
    for n in range(length):
        opts   = letters[n % 2]
        ch     = opts[result % len(opts)]
        if n >= 2 and ch == "g" and name[n-2].lower() == "n":
            ch = "m"
        name  += ch.upper() if n == 0 else ch
        result //= len(opts)
    return name


def index_to_letter(i):
    if i < 26:
        return chr(ord('A') + i)
    return chr(ord('A') + (i // 26) - 1) + chr(ord('A') + (i % 26)) # longer than 26



class SpeciesBundle:
    def __init__(self, sid, name, members, stagnation, is_best, appeared_gen, gen_number):
        self.sid = sid
        self.name = name
        self.members = members
        self.stagnation = stagnation
        self.is_best = is_best
        self.appeared_gen = appeared_gen
        self.gen_number = gen_number

    @property
    def avg_fitness(self):
        if not self.members:
            return 0.0
        total = sum(m[2] for m in self.members)
        return total / len(self.members)

    @property
    def best_fitness(self):
        if not self.members:
            return 0.0
        return self.members[0][2]  # member is sorted and fitness is second index of that tuple



class Creature:
    TORSO_MASS = 2
    LEG_MASS = 1
    MUSCLE_STIFFNESS = 120000
    MUSCLE_DAMPING = 12000

    def __init__(self, space, position, data=None):
        self.space = space
        self.position = list(position)
        self.filter = pymunk.ShapeFilter(group=1)
        self.bodies = {}
        self.shapes = {}
        self.body_list = []
        self.springs = []
        self.spring_joints = []
        self.last_inputs = []
        self.last_outputs = []
        if data is None:
            with open("creatures/creature32.json") as f: # TODO: creature button in menu
                data = json.load(f)

        self.create_bodies(data)
        self.create_joints(data)

    def create_bodies(self, data):
        for bd in data["bodies"]:
            body_type = bd["type"]
            if body_type == "torso":
                mass = self.TORSO_MASS
            elif body_type == "leg":
                mass = self.LEG_MASS
            else:
                print(f"Unknown body type '{body_type}' for '{bd['name']}', defaulting to leg")
                mass = self.LEG_MASS

            size = bd["size"]
            pos = [a + b for a, b in zip(bd["position"], self.position)]

            body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
            body.position = pymunk.Vec2d(*pos)
            body.angular_damping = 0.4

            shape = pymunk.Poly.create_box(body, size)
            shape.friction = 0.8
            shape.collision_type = 2
            shape.filter = self.filter

            self.space.add(body, shape)
            self.bodies[bd["name"]] = body
            self.shapes[bd["name"]] = shape
            self.body_list.append(bd["name"])

    def create_joints(self, data):
        for jd in data["joints"]:
            body1 = self.bodies[jd["body_a"]]
            body2 = self.bodies[jd["body_b"]]
            anchor = [a + b for a, b in zip(jd["anchor"], self.position)]

            joint = pymunk.PivotJoint(body1, body2, anchor)
            self.space.add(joint)

            limit = pymunk.RotaryLimitJoint(body1, body2, math.radians(-135), math.radians(135))
            self.space.add(limit)

            if jd["actuated"]:
                spring = pymunk.DampedRotarySpring(body1, body2, 0, self.MUSCLE_STIFFNESS, self.MUSCLE_DAMPING)
                self.springs.append(spring)
                self.spring_joints.append(joint)
                self.space.add(spring)

    def center_x(self):
        return sum(b.position.x for b in self.bodies.values()) / len(self.bodies)



class Game:
    def __init__(self, render=True):
        self.render = render
        self.width = 1280
        self.height = 720
        self.creatures = []
        self.creature_info = []
        self.species_names = {}
        self.run_salt = random.randint(0, 999_999)
        self._font_cache = {}
        self._ground_cache = {}

        self.gen_history = []
        self.display_gen = -1
        self.auto_advance = True
        self.no_render_mode = False
        self.view_mode = "best"
        self.selected_sid = None
        self.focused_index = 0
        self.follow_best = True
        self.speed_idx = DEFAULT_SPEED_IDX
        self.member_btn_rects = []
        self.config = None
        self.show_joint_labels = True
        self.show_limb_labels = True
        self.show_graph = False

        self.punishment_config = {
            'ground_penalty':   10,
            'rolling_penalty':  100,
            'rolling_threshold': math.pi * 2,
        }

        self.creature_json = None

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            pygame.display.set_caption("Evolution Simulator")
            self.clock = pygame.time.Clock()
        else:
            self.screen = self.clock = None

        self.reset()

    def _font(self, size, bold=False): # optimization so as to not call pygame.font.SysFont one billion times per frame
        key = (size, bold)
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont("Courier New", size, bold=bold)
        return self._font_cache[key]

    # setup stuff

    def reset(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 981)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen) if self.render else None
        self._create_ground()

    def _create_ground(self):
        ground = pymunk.Segment(self.space.static_body, (-1000, 550), (30000, 550), 5)
        ground.friction = 1.0
        ground.collision_type = 1
        self.space.add(ground)

    def spawn_creatures(self, count):
        self.creatures = []
        for _ in range(count):
            creature = Creature(self.space, (0, 400), data=self.creature_json)
            self.creatures.append(creature)

    # viewer

    def _draw_no_render_screen(self):
        self.screen.fill(BG_DARK)
        font_large = self._font(22, bold=True)
        font_small = self._font(13)
        cx, cy  = self.width // 2, self.height // 2

        self.screen.blit(
            font_large.render(f"training gen {len(self.gen_history)}...", True, WHITE),
            font_large.render(f"training gen {len(self.gen_history)}...", True, WHITE).get_rect(center=(cx, cy - 30))
        )

        btn_surf = font_small.render("Resume Rendering", True, (200, 100, 100))
        btn_rect = btn_surf.get_rect(center=(cx, cy + 20))
        self.screen.blit(btn_surf, btn_rect)
        self._no_render_btn_rect = btn_rect.inflate(12, 6)
        pygame.draw.rect(self.screen, (200, 100, 100), self._no_render_btn_rect, width=1, border_radius=4)

        pygame.display.flip()
        self.clock.tick(30)

    def push_and_show(self, bundles):
        for bundle in bundles:
            if bundle.sid not in self.species_names:
                self.species_names[bundle.sid] = generate_name(str(bundle.sid) + str(self.run_salt))
            bundle.name = self.species_names[bundle.sid]

        self.gen_history.append(bundles)
        if len(self.gen_history) > 50:
            self.gen_history.pop(0)
        self.display_gen = len(self.gen_history) - 1

        if self.no_render_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self._no_render_btn_rect and self._no_render_btn_rect.collidepoint(mx, my):
                        self.no_render_mode = False
                        break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.no_render_mode = False
                    break
            else: # still in no render mode
                self._draw_no_render_screen()
                return
        
        self._viewer_loop()

    def _viewer_loop(self):
        while True:
            bundles = self.gen_history[self.display_gen]
            self._setup_display(bundles)
            result = self._run_single_gen(bundles)

            if result == "reload":
                continue
            elif result == "prev":
                self.display_gen = max(0, self.display_gen - 1)
            elif result == "next":
                if self.display_gen < len(self.gen_history) - 1:
                    self.display_gen += 1
                else:
                    return
            elif result == "no_render":
                self.no_render_mode = True
                return
            elif result == "quit":
                pygame.quit()
                sys.exit()

    def _get_selected_bundle(self, bundles):
        for b in bundles:
            if b.sid == self.selected_sid:
                return b
        return bundles[0] if bundles else None

    def _setup_display(self, bundles):
        self.reset()
        self.creature_info = []
        entries = []

        if self.view_mode == "species":
            bundle = self._get_selected_bundle(bundles)
            if not bundle:
                self.view_mode = "best"
                return self._setup_display(bundles)
            for m in bundle.members:
                genome = m[0]
                net = m[1]
                fitness = m[2]
                entries.append((genome,net,fitness, bundle.sid))
        else: # best btn
            for b in bundles:
                if not b.members:
                    continue
                best_member = b.members[0]
                genome = best_member[0]
                net = best_member[1]
                fitness = best_member[2]
                entries.append((genome, net, fitness, b.sid))

        self.spawn_creatures(len(entries))
        for genome, net, fitness, sid in entries:
            self.creature_info.append({'genome': genome, 'net': net, 'fitness': fitness, 'sid': sid})

        self.focused_index = max(0, min(self.focused_index, max(0, len(self.creatures) - 1)))

    # physics helpers

    def touches_ground(self, shape):
        if shape in self._ground_cache:
            return self._ground_cache[shape]
        result = False
        for c in self.space.shape_query(shape):
            if isinstance(c.shape, pymunk.Segment) and c.shape.body == self.space.static_body:
                result = True
                break
        self._ground_cache[shape] = result
        return result

    def get_state(self, creature): # inputs!
        vel_x = vel_y = 0.0
        per_body = []
        for name, body in creature.bodies.items():
            vel_x += body.velocity.x/250
            vel_y += body.velocity.y/250
            per_body += [
                math.sin(body.angle),
                body.angular_velocity / (2 * math.pi),
                float(self.touches_ground(creature.shapes[name])),
            ]
        n = len(creature.bodies)
        return [vel_x / n, vel_y / n] + per_body

    def apply_outputs(self, creature, outputs):
        for spring, value in zip(creature.springs, outputs):
            spring.rest_angle = max(-1.0, min(1.0, value)) * math.pi * 3 / 4 # clamp output value [-1,1]

    # rendering + background elements

    def set_camera(self, target_x):
        sim_w = self.width - LEFT_W - RIGHT_W
        self.draw_options.transform = pymunk.Transform(
            tx=LEFT_W + sim_w // 2 - target_x,
            ty=self.height - 600,
        )

    def draw_ground(self):
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Segment):
                a = self.draw_options.transform @ shape.a
                b = self.draw_options.transform @ shape.b
                pygame.draw.line(self.screen, (200, 200, 200), (a.x, a.y), (b.x, b.y), 3)

    def draw_distance_markers(self):
        interval = 250 # how many pixels to a meter
        font = self._font(14)
        tx = self.draw_options.transform.tx
        first = int(-tx // interval)
        last = int((-tx + self.width) // interval) + 1

        for i in range(first, last):
            if i <= 0:
                continue
            sx = tx + i * interval
            if sx < LEFT_W or sx > self.width - RIGHT_W: # only draw whats on screen
                continue
            gy = 550 + (self.height - 600)
            pygame.draw.line(self.screen, (90, 90, 90), (sx, gy - 40), (sx, gy), 1)       # line
            self.screen.blit(font.render(f"{i}m", True, (90, 90, 90)), (sx + 3, gy - 38)) # text

    def draw_creatures(self, focused_index, display_fitness):
        if not self.creatures:
            return
        focused_x = self.creatures[focused_index].center_x()
        sim_half  = (self.width - LEFT_W - RIGHT_W) / 2
        draw_order = sorted(range(len(self.creatures)), key=lambda i: -abs(self.creatures[i].center_x() - focused_x))

        for i in draw_order:
            creature = self.creatures[i]
            if i == focused_index:
                color = (30, 30, 30)
            else:
                dist = abs(creature.center_x() - focused_x)
                nd = min(1.0, dist / sim_half)
                shade = int(60 + 120 * nd)
                color = (shade, shade, shade)

            for shape in creature.shapes.values():
                                    # if isinstance(shape, pymunk.Poly):
                body  = shape.body  # possible crash
                verts = [body.position + v.rotated(body.angle) for v in shape.get_vertices()]
                verts = [(v.x, v.y) for v in (self.draw_options.transform @ v for v in verts)]
                pygame.draw.polygon(self.screen, color, verts)

        if focused_index < len(self.creatures):
            creature = self.creatures[focused_index]
            if self.show_joint_labels:
                self._draw_spring_labels(creature)
            if self.show_limb_labels:
                self._draw_limb_labels(creature)

    def _draw_spring_labels(self, creature):
        font = self._font(11, bold=True)
        for i, joint in enumerate(creature.spring_joints):
            wp  = joint.a.local_to_world(joint.anchor_a)
            sp  = self.draw_options.transform @ wp
            lbl = font.render(chr(ord('a') + i), True, (220, 80, 220))
            self.screen.blit(lbl, (int(sp.x) + 4, int(sp.y) - 12))

    def _draw_limb_labels(self, creature):
        font = self._font(11, bold=True)
        for i, name in enumerate(creature.body_list): # it'll be in the same order as when we construct the creature, therefore labelled correctly
            body = creature.bodies[name]
            sp = self.draw_options.transform @ body.position
            lbl = font.render(str(i + 1), True, (255, 220, 80))
            self.screen.blit(lbl, (int(sp.x) - lbl.get_width() // 2, int(sp.y) - lbl.get_height() // 2))

    def draw_fps(self):
        self.screen.blit(self._font(14).render(f"FPS: {int(self.clock.get_fps())}", True, WHITE), (LEFT_W + 8, HUD_H + 6))

    def draw_frame_timer(self, physics_steps):
        self.screen.blit(self._font(14).render(f"{physics_steps}/{VIEW_STEPS}", True, DIM), (LEFT_W + 8, HUD_H + 22))

    # simulation controls

    def draw_sim_controls(self):
        sim_right = self.width - RIGHT_W

        #speed slider
        sw, sh = 110, 8
        sx = sim_right - sw - 8
        sy = HUD_H + 8 + sh

        pygame.draw.rect(self.screen, (55, 55, 65), (sx, sy, sw, sh))
        knob_x = sx + (self.speed_idx / (len(SPEEDS) - 1)) * sw
        pygame.draw.circle(self.screen, WHITE, (int(knob_x), sy + sh // 2), 6)

        speed = SPEEDS[self.speed_idx]
        label = f"{speed:.2f}x" if speed < 1 else f"{int(speed)}x"
        speed_lbl = self._font(11).render(f"Speed: {label}", True, WHITE)
        self.screen.blit(speed_lbl, speed_lbl.get_rect(right=sx + sw, bottom=sy - 2))

        slider_rect = pygame.Rect(sx - 4, sy - sh, sw + 8, sh * 4)

        # checkboxes below slider
        cb_y  = sy + sh + 10
        cb_size = 11
        font  = self._font(10)

        joint_rect = self._draw_checkbox(sx, cb_y, self.show_joint_labels, "show joints", font)
        limb_rect  = self._draw_checkbox(sx, cb_y + cb_size + 5, self.show_limb_labels, "show limbs",  font)

        return slider_rect, joint_rect, limb_rect
    
    def _draw_checkbox(self, x, y, checked, label, font):
        cb_size = 11
        box   = pygame.Rect(x, y, cb_size, cb_size)
        pygame.draw.rect(self.screen, (60, 70, 95), box, border_radius=2)
        pygame.draw.rect(self.screen, DIM, box, width=1, border_radius=2)
        if checked:
            pygame.draw.line(self.screen, ACCENT, (x + 2, y + 6), (x + 5, y + 9), 2)
            pygame.draw.line(self.screen, ACCENT, (x + 5, y + 9), (x + 10, y + 3), 2)
        lbl = font.render(label, True, WHITE)
        self.screen.blit(lbl, lbl.get_rect(left=x + cb_size + 4, centery=y + cb_size // 2))
        return pygame.Rect(x - 2, y - 2, cb_size + lbl.get_width() + cb_size, cb_size + 4)
    
    #hud

    def draw_species_hud(self, bundles):
        pygame.draw.rect(self.screen, BG_DARK, (0, 0, self.width, HUD_H))

        # sort by peak fitness for display order
        sorted_bundles = sorted(bundles, key=lambda b: b.best_fitness, reverse=True)

        n = len(sorted_bundles)
        avail_w = self.width - LEFT_W - 280
        slot_w = min(90, avail_w // max(n + 1, 1))
        total_w = (n + 1) * slot_w
        start_x = LEFT_W + (avail_w - total_w) // 2
        slot_h = HUD_H - 10
        pad = 3
        font = self._font(11, bold=True)
        slot_rects = []   # (bundle, rect)

        for i, bundle in enumerate(sorted_bundles):
            x = start_x + i * slot_w
            rect = pygame.Rect(x + pad, 5, slot_w - pad * 2, slot_h)

            pygame.draw.rect(self.screen, (42, 41, 52), rect, border_radius=4)
            pygame.draw.rect(self.screen, (80, 80, 90), rect, width=2, border_radius=4)
            lbl = font.render(bundle.name, True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=rect.center))
            slot_rects.append((bundle, rect))

            if self.view_mode == "species" and bundle.sid == self.selected_sid:
                pygame.draw.line(self.screen, ACCENT, (rect.left + 3, rect.bottom + 2), (rect.right - 3, rect.bottom + 2), 2)

        # best button wow this code sucks ngl xd
        bx = start_x + n * slot_w
        best_rect = pygame.Rect(bx + pad, 5, slot_w - pad * 2, slot_h)
        pygame.draw.rect(self.screen, (42, 41, 52), best_rect, border_radius=4)
        pygame.draw.rect(self.screen, (80, 80, 90), best_rect, width=2, border_radius=4)
        self.screen.blit(font.render("BEST", True, WHITE), font.render("BEST", True, WHITE).get_rect(center=best_rect.center))
        if self.view_mode == "best":
            pygame.draw.line(self.screen, ACCENT, (best_rect.left + 3, best_rect.bottom + 2), (best_rect.right - 3, best_rect.bottom + 2), 2)

        return slot_rects, best_rect

    def draw_hud_controls(self):
        font = self._font(11, bold=True)
        fontsmall = self._font(11)
        cy = HUD_H // 2

        # gen buttons
        prev_surf = font.render("<", True, DIM)
        next_surf = font.render(">", True, DIM)
        gen_surf  = font.render(f"{str(self.display_gen+1)}/{str(len(self.gen_history))}", True, WHITE)

        rx = self.width - 10
        nx = rx - next_surf.get_width()
        gx = nx - gen_surf.get_width() - 8
        px = gx - prev_surf.get_width() - 8

        self.screen.blit(next_surf, next_surf.get_rect(centery=cy, left=nx))
        self.screen.blit(gen_surf, gen_surf.get_rect(centery=cy, left=gx))
        self.screen.blit(prev_surf, prev_surf.get_rect(centery=cy, left=px))

        prev_rect = prev_surf.get_rect(centery=cy, left=px).inflate(6, 6)
        next_rect = next_surf.get_rect(centery=cy, left=nx).inflate(6, 6)

        # autogen checkbox
        box_size = 12
        lbl_surf = fontsmall.render("Automatic Generations", True, WHITE)
        total_cb = box_size + 5 + lbl_surf.get_width()
        bx = px - total_cb - 14
        by = cy - box_size // 2
        auto_rect = self._draw_checkbox(bx, by, self.auto_advance, "Automatic Generations", fontsmall)

        # no render button
        nr_surf = fontsmall.render("No Render", True, (200, 100, 100))
        nr_x = bx - nr_surf.get_width() - 16
        self.screen.blit(nr_surf, nr_surf.get_rect(centery=cy, left=nr_x))
        no_render_rect = nr_surf.get_rect(centery=cy, left=nr_x).inflate(6, 4)

        # export button
        exp_surf = fontsmall.render("Export", True, (100, 180, 255))
        exp_x = 9
        self.screen.blit(exp_surf, exp_surf.get_rect(centery=cy, left=exp_x))
        export_rect = exp_surf.get_rect(centery=cy, left=exp_x).inflate(6, 4)

        return prev_rect, next_rect, auto_rect, no_render_rect, export_rect
    
    # info helper
    
    def _draw_info_row(self, x, y, key, font, color=WHITE):
        k_surf = font.render(key, True, color)
        self.screen.blit(k_surf, (x, y))
        return y + k_surf.get_height() + 3

    # species info

    def draw_left_panel(self, bundles):
        self.member_btn_rects = []

        pygame.draw.rect(self.screen, PANEL_BG, (0, HUD_H, LEFT_W, self.height - HUD_H))
        pygame.draw.line(self.screen, (45, 55, 85), (LEFT_W, HUD_H), (LEFT_W, self.height), 1)

        pad = 9
        y = HUD_H + pad
        fontsmall = self._font(11)
        fontmedium = self._font(12, bold=True)
        fontlarge = self._font(15, bold=True)

        if self.view_mode == "species":
            bundle = self._get_selected_bundle(bundles)
            if not bundle:
                return

            y = self._draw_info_row(pad, y, bundle.name, fontlarge)
            if bundle.is_best:
                y = self._draw_info_row(pad,y,f"Stagnation : {bundle.stagnation}/15 (safe)", fontsmall)
            else:
                y = self._draw_info_row(pad,y,f"Stagnation : {bundle.stagnation}/15", fontsmall)
            y = self._draw_info_row(pad,y,f"Avg Fitness : {bundle.avg_fitness:.1f}", fontsmall)
            y = self._draw_info_row(pad,y,f"Peak Fitness : {bundle.best_fitness:.1f}", fontsmall)
            y = self._draw_info_row(pad,y,f"Appeared : Gen. {bundle.appeared_gen}", fontsmall)

            # placement by peak fitness
            sorted_bundles = sorted(bundles, key=lambda b: b.best_fitness, reverse=True)
            rank_map = {}
            for i,b in enumerate(sorted_bundles):
                rank_map[b.sid] = i + 1

            rank = rank_map.get(bundle.sid, "?") # if cant find for some reason return "?"
            y = self._draw_info_row(pad,y,f"Placement : #{rank}", fontsmall)
            y += 6

            n_members = len(bundle.members)
            cols = 3
            rows = math.ceil(n_members / cols)
            avail_h = self.height - y - pad
            btn_width = (LEFT_W - pad*2) // cols
            btn_height = min(btn_width, avail_h // max(rows, 1))

            for i, (genome, net, fitness) in enumerate(bundle.members):
                col = i % cols
                row = i // cols
                bx = pad + col * btn_width
                by = y + row * (btn_height + 2) 
                if by + btn_height > self.height - pad:
                    break
                rect = pygame.Rect(bx, by, btn_width - 2, btn_height - 2)

                focused = (i == self.focused_index)
                pygame.draw.rect(self.screen, (50, 80, 130) if focused else (38, 50, 80), rect, border_radius=3)
                pygame.draw.rect(self.screen, WHITE if focused else (70, 85, 115), rect, width=1, border_radius=3)

                name_surf = fontsmall.render(bundle.name, True, (200, 200, 200))
                letter_surf = fontmedium.render(index_to_letter(i), True, WHITE)
                self.screen.blit(name_surf, name_surf.get_rect(centerx=rect.centerx, top=rect.top + 3))
                self.screen.blit(letter_surf, letter_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 3))
                self.member_btn_rects.append(rect)

        else:  # best mode
            y = self._draw_info_row(pad,y,"Best of each Species", fontlarge)
            y += 6

            sorted_bundles = sorted(bundles, key=lambda b: b.best_fitness, reverse=True)
            n_bundles = len(sorted_bundles)
            cols = 3
            rows = math.ceil(n_bundles / cols)
            avail_h = self.height - y - pad
            btn_width = (LEFT_W - pad*2) // cols
            btn_height = min(btn_width, avail_h // max(rows, 1))

            for i, bundle in enumerate(sorted_bundles):
                col = i % cols
                row = i // cols
                bx = pad + col * btn_width
                by = y + row * (btn_height + 2)
                if by + btn_height > self.height - pad:
                    break
                rect = pygame.Rect(bx, by, btn_width - 2, btn_height - 2)

                orig_idx = bundles.index(bundle)
                focused = (orig_idx == self.focused_index and not self.follow_best)
                if focused:
                    pygame.draw.rect(self.screen, (50, 80, 130), rect, border_radius=3)
                    pygame.draw.rect(self.screen, WHITE, rect, width=1, border_radius=3)
                else:
                    pygame.draw.rect(self.screen, (38, 50, 80), rect, border_radius=3)
                    pygame.draw.rect(self.screen, (70, 85, 115), rect, width=1, border_radius=3)

                apex_surf = fontsmall.render("Apex", True, (180, 200, 230))
                name_surf = fontmedium.render(bundle.name, True, WHITE)
                self.screen.blit(apex_surf, apex_surf.get_rect(centerx=rect.centerx, top=rect.top + 3))
                self.screen.blit(name_surf, name_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 3))
                self.member_btn_rects.append((orig_idx, rect))

    # creature info

    def draw_right_panel(self, bundles, display_fitness):
        px = self.width - RIGHT_W
        pygame.draw.rect(self.screen, PANEL_BG, (px, HUD_H, RIGHT_W, self.height - HUD_H))
        pygame.draw.line(self.screen, (45, 55, 85), (px, HUD_H), (px, self.height), 1)

        if not self.creatures or self.focused_index >= len(self.creature_info):
            return

        pad = 9
        y = HUD_H + pad
        x = px + pad
        fontsmall = self._font(11)
        fontmedium = self._font(12)

        info = self.creature_info[self.focused_index]
        genome = info['genome']
        sid = info['sid']
        if self.focused_index < len(display_fitness):
            dist = dist = display_fitness[self.focused_index] / 250
        else:
            dist = 0
        fitness = info['fitness']

        species_name = next((b.name for b in bundles if b.sid == sid), "?")
        appeared = getattr(genome, 'appeared_gen', '?')

        # overall rank across gen
        all_members = []
        for b in bundles:
            for genome_m, net_m, fit_m in b.members:
                all_members.append(fit_m)
        all_members.sort(reverse=True)
        overall_rank = 1
        for f in all_members:
            if f > fitness:
                overall_rank += 1
            else:
                break

        # in-species rank
        if self.view_mode == "species":
            species_rank = self.focused_index + 1
        else:
            species_rank = None

        lbl = self._font(13, bold=True).render("CREATURE", True, WHITE)
        self.screen.blit(lbl, (x, y))
        y += lbl.get_height()
        y += 6

        y = self._draw_info_row(x,y,f"Species : {species_name}", fontsmall)
        y = self._draw_info_row(x,y,f"Distance : {dist:.2f}m", fontsmall)
        y = self._draw_info_row(x,y,f"Fitness :{fitness:.2f}", fontsmall)
        y = self._draw_info_row(x,y,f"Overall : #{overall_rank}", fontsmall)
        if species_rank is not None:
            y = self._draw_info_row(x,y,f"In Species : #{species_rank}", fontsmall)
        y = self._draw_info_row(x,y,f"Appeared : Gen. {appeared}", fontsmall)
        y += 8

        if genome:
            net_rect = pygame.Rect(x, y, RIGHT_W - pad * 2, self.height - y - pad)
            creature = self.creatures[self.focused_index]
            self._draw_neural_net(genome, creature.last_inputs, creature.last_outputs, net_rect)

    def _draw_neural_net(self, genome, last_inputs, last_outputs, rect):
        if not self.config:
            return

        input_keys  = self.config.genome_config.input_keys
        output_keys = self.config.genome_config.output_keys
        hidden_keys = [k for k in genome.nodes if k not in output_keys]

        body_count   = (len(input_keys) - 2) // 3
        input_labels = ["vel_x", "vel_y"]
        for b in range(body_count):
            input_labels += [f"ang{b+1}", f"spd{b+1}", f"gnd{b+1}"]

        input_key_set = set(input_keys)
        output_key_set = set(output_keys)
        connected_inputs = set()
        connected_outputs = set()
        for cg in genome.connections.values():
            if not cg.enabled:
                continue
            k_in, k_out = cg.key
            if k_in in input_key_set: connected_inputs.add(k_in)
            if k_out in output_key_set: connected_outputs.add(k_out)
        
        visible_inputs = []
        for k in input_keys:
            if k in connected_inputs:
                visible_inputs.append(k)
        
        visible_outputs = []
        for k in output_keys:
            if k in connected_outputs:
                visible_outputs.append(k)

        node_r = 5
        font = self._font(9)

        legend_h  = 34
        draw_rect = pygame.Rect(rect.left, rect.top, rect.width, rect.height - legend_h - 32)

        def y_positions(keys, rect):
            if not keys: return {}
            if len(keys) == 1:
                return {keys[0]: rect.top + rect.height // 2}
            
            total_h = rect.height - node_r * 2
            return {k: rect.top + node_r + i * total_h // (len(keys) - 1) for i, k in enumerate(keys)}

        ix = draw_rect.left + node_r + 4
        ox = draw_rect.right - node_r - 18
        hx = (ix + ox) // 2

        node_pos_map = {}

        layers = [
            (ix, visible_inputs),
            (hx, hidden_keys),
            (ox, visible_outputs)
        ]

        for x, keys in layers: 
            for k, y in y_positions(keys, draw_rect).items():
                node_pos_map[k] = (x,y)

        ly = draw_rect.bottom + 16
        self._draw_legend(rect.left, ly, "act", ACT_COLORS, font)
        self._draw_legend(rect.left, ly + 16, "agg", AGG_COLORS, font)

        for cg in genome.connections.values():
            if not cg.enabled:
                continue
            k_in, k_out = cg.key
            if k_in not in node_pos_map or k_out not in node_pos_map:
                continue
            x1, y1 = node_pos_map[k_in]
            x2, y2 = node_pos_map[k_out]
            if k_out in genome.nodes:
                act = genome.nodes[k_out].activation
                color = ACT_COLORS.get(act, DEFAULT_ACT_COLOR)
            else:
                color = DEFAULT_ACT_COLOR
            pygame.draw.line(self.screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 1)

        for i, k in enumerate(input_keys):
            if k not in node_pos_map:
                continue
            nx, ny = node_pos_map[k]
            val = last_inputs[i] if i < len(last_inputs) else 0
            shade = int(220 * max(0.0, min(1.0, (val + 1) / 2)))

            pygame.draw.circle(self.screen, (shade, shade, shade), (int(nx), int(ny)), node_r)
            pygame.draw.circle(self.screen, DIM, (int(nx), int(ny)), node_r, 1)

            label_str = input_labels[i] if i < len(input_labels) else f"in{i}"
            lbl_surf = font.render(label_str, True, DIM)
            self.screen.blit(lbl_surf, lbl_surf.get_rect(centerx=int(nx), top=int(ny) + node_r + 1))

        for k in hidden_keys:
            if k not in node_pos_map:
                continue
            nx, ny = node_pos_map[k]
            agg = genome.nodes[k].aggregation if k in genome.nodes else "sum"
            col = AGG_COLORS.get(agg, DEFAULT_AGG_COLOR)
            pygame.draw.circle(self.screen, col, (int(nx), int(ny)), node_r)

        for i, k in enumerate(output_keys):
            if k not in node_pos_map:
                continue
            nx, ny = node_pos_map[k]
            agg = genome.nodes[k].aggregation if k in genome.nodes else "sum"
            col = AGG_COLORS.get(agg, DEFAULT_AGG_COLOR)
            pygame.draw.circle(self.screen, col, (int(nx), int(ny)), node_r)
            val = max(-1.0, min(1.0, last_outputs[i])) if i < len(last_outputs) else 0
            letter_lbl = font.render(chr(ord('a') + i), True, WHITE)
            self.screen.blit(letter_lbl, (int(nx) + node_r + 1, int(ny) - node_r))
            val_lbl = font.render(f"{val:.1f}", True, DIM)
            self.screen.blit(val_lbl, val_lbl.get_rect(centerx=int(nx), top=int(ny) + node_r + 1))

    def _draw_legend(self, x, y, prefix, color_map, font):
        surf = font.render(f"{prefix}: ", True, DIM)
        self.screen.blit(surf, (x, y))
        cx = x + surf.get_width()
        for name, col in color_map.items():
            lbl = font.render(name, True, col)
            self.screen.blit(lbl, (cx, y))
            cx += lbl.get_width() + 4

    # sim loop
 
    def _run_single_gen(self, bundles): # returns what to do next in loop
        physics_steps   = 0
        step_acc        = 0.0
        start_x         = [c.center_x() for c in self.creatures]
        display_fitness = [0.0] * len(self.creatures)
        best_btn_rect   = None
        slot_rects      = []
        slider_rect     = pygame.Rect(0, 0, 1, 1) # initialize to avoid crashes when clicking in between frames
        joint_cb_rect   = pygame.Rect(0, 0, 1, 1)
        limb_cb_rect    = pygame.Rect(0, 0, 1, 1)
        export_rect = pygame.Rect(0, 0, 1, 1)

        while True:
            self.clock.tick(TARGET_FPS)

            self._ground_cache.clear()

            step_acc += SPEEDS[self.speed_idx]
            while step_acc >= 1.0:
                self.space.step(1 / TARGET_FPS)
                self._ground_cache.clear()
                for i, (creature, info) in enumerate(zip(self.creatures, self.creature_info)):
                    inputs  = self.get_state(creature)
                    outputs = info['net'].activate(inputs)
                    creature.last_inputs  = inputs
                    creature.last_outputs = outputs
                    self.apply_outputs(creature, outputs)
                physics_steps += 1
                step_acc -= 1.0

            for i, creature in enumerate(self.creatures):
                display_fitness[i] = creature.center_x() - start_x[i]

            if self.follow_best and self.creatures: # best btn
                self.focused_index = display_fitness.index(max(display_fitness))
            self.focused_index = max(0, min(self.focused_index, max(0, len(self.creatures) - 1)))

            if self.creatures:
                self.set_camera(self.creatures[self.focused_index].center_x())

            # draw game
            self.screen.fill(BACKGROUND)
            self.draw_ground()
            self.draw_distance_markers()
            self.draw_creatures(self.focused_index, display_fitness)

            # draw hud

            self.draw_left_panel(bundles)
            self.draw_right_panel(bundles, display_fitness)
            slot_rects, best_btn_rect = self.draw_species_hud(bundles)
            prev_rect, next_rect, auto_rect, no_render_rect, export_rect = self.draw_hud_controls()
            slider_rect, joint_cb_rect, limb_cb_rect = self.draw_sim_controls()
            self.draw_fps()
            self.draw_frame_timer(physics_steps)

            pygame.display.flip()

            # controls

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if slider_rect.collidepoint(mx, my):
                    t = (mx - slider_rect.x) / max(1, slider_rect.width)
                    self.speed_idx = max(0, min(len(SPEEDS) - 1, int(t * len(SPEEDS))))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.follow_best   = False
                        self.focused_index = (self.focused_index - 1) % max(1, len(self.creatures))
                    if event.key == pygame.K_RIGHT:
                        self.follow_best   = False
                        self.focused_index = (self.focused_index + 1) % max(1, len(self.creatures))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()

                    if joint_cb_rect.collidepoint(mx, my):
                        self.show_joint_labels = not self.show_joint_labels
                    if limb_cb_rect.collidepoint(mx, my):
                        self.show_limb_labels = not self.show_limb_labels
                    if prev_rect.collidepoint(mx, my):
                        return "prev"
                    if next_rect.collidepoint(mx, my):
                        return "next"
                    if auto_rect.collidepoint(mx, my):
                        self.auto_advance = not self.auto_advance
                    if no_render_rect.collidepoint(mx, my):
                        return "no_render"
                    if export_rect.collidepoint(mx, my):
                        self._export_state()

                    if best_btn_rect and best_btn_rect.collidepoint(mx, my):
                        self.view_mode   = "best"
                        self.follow_best = True
                        return "reload"

                    for bundle, rect in slot_rects:
                        if rect.collidepoint(mx, my):
                            self.selected_sid  = bundle.sid
                            self.view_mode     = "species"
                            self.focused_index = 0
                            self.follow_best   = False
                            return "reload"

                    for item in self.member_btn_rects:
                        if isinstance(item, tuple):
                            orig_idx, rect = item
                        else:
                            orig_idx = self.member_btn_rects.index(item)
                            rect = item
                        if rect.collidepoint(mx, my):
                            self.focused_index = orig_idx
                            self.follow_best   = False

            if physics_steps >= VIEW_STEPS:
                if self.auto_advance:
                    return "next"
                else:
                    return "reload"

    # eval

    def run_genome(self, net):
        self.reset()
        self.spawn_creatures(1)
        creature = self.creatures[0]
        start_x = creature.center_x()

        ground_penalty = 0
        rolling_penalty = 0

        for _ in range(EVAL_STEPS):
            self._ground_cache.clear()
            self.space.step(1 / TARGET_FPS)
            inputs = self.get_state(creature)
            outputs = net.activate(inputs)
            self.apply_outputs(creature, outputs)

            for name, shape in creature.shapes.items():
                if "torso" in name:
                    if self.touches_ground(shape): #  yk usually creature's torsos dont touch the ground when they walk, so let's penalize that
                        ground_penalty += self.punishment_config['ground_penalty']
                    if abs(creature.bodies[name].angle) > self.punishment_config['rolling_threshold']: # no rolling, rolling isnt walking!
                        rolling_penalty += self.punishment_config['rolling_penalty']

        fitness = creature.center_x() - start_x - ground_penalty - rolling_penalty
        return fitness / 100
    
    # export
    
    def _export_state(self):
            import time
    
            os.makedirs("states", exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = f"states/state_{timestamp}.pkl"
            data = {
                'gen_history': self.gen_history,
                'species_names': self.species_names,
                'display_gen': self.display_gen,
                'creature_json': self.creature_json,
                'neat_config': self._neat_config_text,
                'punishment_config': self.punishment_config,
            }
            with open(path, 'wb') as f:
                pickle.dump(data, f)

    def load_state(self, path):
        import tempfile, neat
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.gen_history = data['gen_history']
        self.species_names = data['species_names']
        self.display_gen = data['display_gen']
        self.punishment_config = data.get('punishment_config', self.punishment_config)
        if isinstance(data['creature_json'], dict):
            self.creature_json = data['creature_json']
        else:
            self.creature_json = json.loads(data['creature_json'])

        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg")
        tmp.write(data['neat_config'])
        tmp.close()
        self.config = neat.Config(
            neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            tmp.name,
        )
        os.unlink(tmp.name)
        # re-assign names since bundles are already in history
        for bundles in self.gen_history:
            for bundle in bundles:
                bundle.name = self.species_names.get(bundle.sid, "?")
