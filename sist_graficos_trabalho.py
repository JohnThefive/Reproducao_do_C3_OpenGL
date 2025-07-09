import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ----- Funções de transformação ----- #
def translate(dx, dy, dz):
    t = np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1],
    ])
    return t

def scale(sx, sy, sz):
    e = np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1],
    ])
    return e

def rotate_x(alfa):
    cosseno = np.cos(alfa)
    seno = np.sin(alfa)
    r = np.array([
     [1, 0,          0, 0],
     [0, cosseno, -seno, 0],
     [0, seno, cosseno, 0],
     [0, 0, 0, 1]
    ])
    return r


def rotate_y(alfa):
    cosseno = np.cos(alfa)
    seno = np.sin(alfa)
    r = np.array([
     [cosseno,0,seno, 0],
     [0, 1, 0, 0],
     [-seno, 0, cosseno, 0],
     [0, 0, 0, 1]
    ])
    return r

def rotate_z(alfa):
    cosseno = np.cos(alfa)
    seno = np.sin(alfa)
    r = np.array([
     [cosseno, -seno,   0, 0],
     [seno,    cosseno, 0, 0],
     [0,       0,       1, 0],
     [0, 0, 0, 1]
    ])
    return r


#Funcao perspectiva:
def perspectiva(fovy, aspect, near, far):
    fovy_rad = np.radians(fovy)
    t = near * np.tan(fovy_rad / 2.0)
    b = -t
    r = t * aspect
    l = -r
    n = near
    f = far
    
    matriz = np.zeros((4, 4), dtype=np.float32)
    matriz[0, 0] = n / r
    matriz[1, 1] = n / t
    matriz[2, 2] = -(f + n) / (f - n)
    matriz[2, 3] = -(2 * f * n) / (f - n)
    matriz[3, 2] = -1.0
    return matriz

def orthographic(right, left, bottom, top, near, far):
    matrix = np.zeros((4,4))
    matrix[0, 0] = 2 / (right - left)
    matrix[0, 3] = -((right + left) / (right - left))
    matrix[1, 1] = 2 / (top - bottom)
    matrix[1, 3] = - ((top + bottom) / (top - bottom))
    matrix[2, 2] = -2 / (far - near)
    matrix[2, 3] = - ((far + near) / (far - near))
    matrix[3, 3] = 1
    return matrix

def bresenham(x0, x1, y0, y1):
    points = []
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return points

#funcao que calcula a normal:
def calcular_normal(v0, v1, v2):
    a = np.array(v1) - np.array(v0)
    b = np.array(v2) - np.array(v0)
    normal = np.cross(a, b)
    norma = np.linalg.norm(normal)
    if norma == 0:
        return np.array([0.0, 0.0, 1.0]) 
    return normal / norma

def draw_cube(colors = None):
    vertices_cubo = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), 
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), 
    ]
    faces_cubo = [
        (4, 5, 6, 7), (1, 0, 3, 2), (0, 4, 7, 3), 
        (5, 1, 2, 6), (7, 6, 2, 3), (1, 5, 4, 0)
    ]
    glBegin(GL_QUADS)
    for i, face in enumerate(faces_cubo):
        v0, v1, v2 = vertices_cubo[face[0]], vertices_cubo[face[1]], vertices_cubo[face[2]]
        normal = calcular_normal(v0, v1, v2)
        glNormal3fv(normal)
        if colors and len(colors) == 6:
            glColor3fv(colors[i])
        for vertice_index in face:
            glVertex3fv(vertices_cubo[vertice_index])
    glEnd()
    
def draw_hex():
    radius, height, num_lados = 1, 1, 6
    angulos = np.linspace(0, 2 * np.pi, num=num_lados, endpoint=False)
    base = np.array([[radius * np.cos(a), radius * np.sin(a), 0] for a in angulos])
    topo = base + np.array([0, 0, height])
    
    glNormal3f(0.0, 0.0, -1.0) 
    glBegin(GL_POLYGON)
    for v in reversed(base):
        glVertex3fv(v)
    glEnd()

    glNormal3f(0.0, 0.0, 1.0)
    glBegin(GL_POLYGON)
    for v in topo:
        glVertex3fv(v)
    glEnd()

    glBegin(GL_QUADS)
    for i in range(num_lados):
        v1, v2 = base[i], topo[i]
        v3, v4 = topo[(i + 1) % num_lados], base[(i + 1) % num_lados]
        normal_lateral = calcular_normal(v1, v4, v2)
        glNormal3fv(normal_lateral)
        glVertex3fv(v1); glVertex3fv(v2); glVertex3fv(v3); glVertex3fv(v4)
    glEnd()
    
def draw_c(center_x=0, center_y=0, inner_radius=15, thickness=8, num_segments=30):
    outer_radius = inner_radius + thickness
    all_pixels = set()

    start_angle, end_angle = np.radians(45), np.radians(315)
    angles = np.linspace(start_angle, end_angle, num_segments)
    
    inner_points = [(inner_radius * np.cos(a), inner_radius * np.sin(a)) for a in angles]
    outer_points = [(outer_radius * np.cos(a), outer_radius * np.sin(a)) for a in angles]

    # Desenha os arcos interno e externo
    for i in range(len(angles) - 1):
        all_pixels.update(bresenham(inner_points[i][0], inner_points[i+1][0], inner_points[i][1], inner_points[i+1][1]))
        all_pixels.update(bresenham(outer_points[i][0], outer_points[i+1][0], outer_points[i][1], outer_points[i+1][1]))
    
    all_pixels.update(bresenham(inner_points[0][0], outer_points[0][0], inner_points[0][1], outer_points[0][1]))
    all_pixels.update(bresenham(inner_points[-1][0], outer_points[-1][0], inner_points[-1][1], outer_points[-1][1]))

    glBegin(GL_QUADS)
    for x, y in all_pixels:
        px, py = x + center_x, y + center_y
        glVertex2f(px, py); glVertex2f(px + 1, py); glVertex2f(px + 1, py + 1); glVertex2f(px, py + 1)
    glEnd()
    
def draw_ground_circle(radius, num_segments=100):
    glBegin(GL_TRIANGLE_FAN)
    
    # A normal para um chão plano aponta para cima (eixo Y positivo)
    glNormal3f(0.0, 1.0, 0.0)
    
    # Vértice central do círculo (origem)
    glVertex3f(0.0, 0.0, 0.0)
    
    # Cria os vértices na circunferência
    for i in range(num_segments + 1):
        angle = 2 * np.pi * i / num_segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        glVertex3f(x, 0.0, z)
        
    glEnd()

def apply_matrix(matriz):
    glMultMatrixf(matriz.T)

def main():
    pygame.init()
    
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
    
    luz_ambiente, luz_difusa, luz_especular = [0.3, 0.3, 0.3, 1.0], [0.8, 0.8, 0.8, 1.0], [1.0, 1.0, 1.0, 1.0]
    posicao_luz, material_especular, material_shininess = [5.0, 10.0, 10.0, 1.0], [1.0, 1.0, 1.0, 1.0], [50.0]
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente); glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular); glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    
    pygame.display.set_caption("Predio C3 - Pressione 'P' (Perspectiva) ou 'O' (Ortogonal)")
    projection_mode = 'perspective'
    
    yaw, pitch, distance = 0.0, 25.0, 25.0
    mouse_down = False 

    COR_MARROM = (0.5, 0.25, 0.0)
    COR_BRANCO = (1.0, 1.0, 1.0)
    PALETA_MARROM_TETO_BRANCO = [COR_BRANCO, COR_BRANCO, COR_MARROM, COR_MARROM, COR_MARROM, COR_MARROM]
    
    MAT_GRAMA_VERDE = {
        "ambient":  [0.0, 0.2, 0.0, 1.0],
        "diffuse":  [0.1, 0.6, 0.1, 1.0],
        "specular": [0.05, 0.05, 0.05, 1.0],
        "shininess": 10.0
    }
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: projection_mode = 'perspective'
                elif event.key == pygame.K_o: projection_mode = 'orthogonal'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down, _ = True, pygame.mouse.get_rel()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            elif event.type == pygame.MOUSEWHEEL:
                distance = np.clip(distance - event.y * 1.5, 1.0, 80.0)

        if mouse_down:
            dx, dy = pygame.mouse.get_rel()
            yaw += dx * 0.5
            pitch = np.clip(pitch - dy * 0.5, -89, 89)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        aspect, near, far = display[0] / display[1], 0.1, 100.0
        if projection_mode == 'perspective':
            apply_matrix(perspectiva(60, aspect, near, far))
        else:
            ortho_height = distance * 0.5
            apply_matrix(orthographic(-ortho_height*aspect, ortho_height*aspect, -ortho_height, ortho_height, near, far))
        
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        rad_yaw, rad_pitch = np.radians(yaw), np.radians(pitch)
        cam_x = distance * np.cos(rad_pitch) * np.sin(rad_yaw)
        cam_y = distance * np.sin(rad_pitch)
        cam_z = distance * np.cos(rad_pitch) * np.cos(rad_yaw)
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)

        # ----- DESENHO DA CENA -----
        # Cubo central c3
        glPushMatrix()
        apply_matrix(scale(4, 6, 3))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # Retangulo maior
        glPushMatrix()
        apply_matrix(scale(12, 4, 3))
        apply_matrix(translate(-0.335, 1.5, 0))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # Bloco da direita
        glPushMatrix()
        glColor3fv(COR_BRANCO); apply_matrix(scale(4, 4, 3)); apply_matrix(translate(2, 1.5, 0))
        apply_matrix(rotate_z(np.radians(20))); draw_cube()
        glPopMatrix()
        glPushMatrix()
        apply_matrix(scale(3, 3, 3)); apply_matrix(translate(3.7, 2.7, 0))
        apply_matrix(rotate_z(np.radians(20))); draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # Bloco da esquerda
        glPushMatrix()
        glColor3fv(COR_BRANCO); apply_matrix(scale(4, 4, 3)); apply_matrix(translate(-1, 1.5, 0))
        apply_matrix(rotate_z(np.radians(70))); draw_cube()
        glPopMatrix()
        glPushMatrix()
        apply_matrix(scale(3, 3, 3)); apply_matrix(translate(-2.35, 2.7, 0))
        apply_matrix(rotate_z(np.radians(70))); draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # Hall hexagonal
        glPushMatrix()
        glColor3fv(COR_BRANCO); apply_matrix(scale(2.5, 2.5, 3))
        apply_matrix(translate(0.78, -0.35, 0.01)); draw_hex()
        glPopMatrix()
        
        # Blocos do hall
        glPushMatrix()
        apply_matrix(scale(3, 3, 3)); apply_matrix(translate(-0.18, -1.7, 0))
        apply_matrix(rotate_z(np.radians(45))); draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        glPushMatrix()
        apply_matrix(scale(3, 3, 3)); apply_matrix(translate(1.48, -0.3, 0))
        apply_matrix(rotate_z(np.radians(-135))); draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # Letra 'C'
        glPushMatrix()
        glColor3fv(COR_BRANCO)
        apply_matrix(translate(5.3, -4.3, 1.8))
        apply_matrix(scale(0.02, 0.02, 0.02))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(rotate_y(np.radians(45)))
        draw_c(inner_radius=20, thickness=10, num_segments=40)
        glPopMatrix()
        
        # Carácter '3'
        glPushMatrix()
        glColor3fv(COR_BRANCO)
        apply_matrix(translate(5.8, -3.8, 2.05))
        apply_matrix(scale(0.01, 0.01, 0.01))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(rotate_y(np.radians(45)))
        apply_matrix(rotate_z(np.radians(180)))
        draw_c(inner_radius=20, thickness=10, num_segments=40)
        glPopMatrix()
        
        glPushMatrix()
        glColor3fv(COR_BRANCO)
        apply_matrix(translate(5.8, -3.8, 1.6))
        apply_matrix(scale(0.01, 0.01, 0.01))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(rotate_y(np.radians(45)))
        apply_matrix(rotate_z(np.radians(180)))
        draw_c(inner_radius=20, thickness=10, num_segments=40)
        glPopMatrix()
        
        glPushMatrix()
        apply_matrix(translate(2.0, 5.0, 0.0))
        apply_matrix(rotate_x(np.radians(90)))
        draw_ground_circle(radius=18) 
        glPopMatrix() 
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()