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

def draw_grid(size=2000, step=2):
    glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_LINES)
    for i in range(-size//2, size//2 + 1, step):
        # Linhas verticais
        glVertex3f(i, -size//2, 0)
        glVertex3f(i, size//2, 0)
        # Linhas horizontais
        glVertex3f(-size//2, i, 0)
        glVertex3f(size//2, i, 0)
    glEnd()

def draw_axes(length=100):
    glBegin(GL_LINES)
    # X - vermelho
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)
    # Y - verde
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, length, 0)
    # Z - azul
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, length)
    glEnd()
    
def apply_matrix(matriz):
    glMultMatrixf(matriz.T)
    
def draw_cube():
    #define os vértices do losango (x, y, z) 
    vertices_cubo = [
        (0, 0, 0), 
        (1, 0, 0), 
        (1, 1, 0), 
        (0, 1, 0), 
        (0, 0, 1), 
        (1, 0, 1), 
        (1, 1, 1), 
        (0, 1, 1), 
    ]
    arestas_cubo =    [ (0, 1), (1, 2), (2, 3), (3, 0), 
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)] 

    # Começa a desenhar um polígono
    glBegin(GL_LINES)
    
    # Define a cor do losango (RGBA: vermelho)
    glColor3f(1.0, 0.0, 0.0)
    
    # Desenha cada vértice
    for i in arestas_cubo:
        for j in i:
            glVertex3fv(vertices_cubo[j])
            
    
    # Termina de desenhar o polígono
    glEnd()
    
def draw_hex():
    radius = 1
    height = 1
    num_lados = 6
    angulos = np.linspace(0, 2 * np.pi, num=num_lados, endpoint=False)

    # Gerar vértices da base e do topo
    base = np.array([[radius * np.cos(a), radius * np.sin(a), 0] for a in angulos])
    topo = base + np.array([0, 0, height])  # mesma base + altura em Z

    # Desenha as arestas da base
    glColor3f(0.0, 0.6, 1.0)
    glBegin(GL_LINE_LOOP)
    for v in base:
        glVertex3fv(v)
    glEnd()

    # Desenha as arestas do topo
    glBegin(GL_LINE_LOOP)
    for v in topo:
        glVertex3fv(v)
    glEnd()

    # Liga base ao topo com linhas verticais
    glBegin(GL_LINES)
    for i in range(num_lados):
        glVertex3fv(base[i])
        glVertex3fv(topo[i])
    glEnd()

def apply_camera(pos, look, up):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(*pos, *look, *up)
    
def get_direction(yaw, pitch):
    rad_yaw = np.radians(yaw)
    rad_pitch = np.radians(pitch)
    x = np.cos(rad_pitch) * np.cos(rad_yaw)
    y = np.sin(rad_pitch)
    z = np.cos(rad_pitch) * np.sin(rad_yaw)
    return np.array([x, y, z], dtype=np.float32)

def visualize_z_buffer(width, height):
    z_buffer_data = glReadPixels(0, 0, width, height, GL_DEPTH_COMPONENT, GL_FLOAT)
    depth_map = np.frombuffer(z_buffer_data, dtype=np.float32).reshape(height, width)
    depth_map = np.power(depth_map, 0.2) 
    depth_map = np.flipud(depth_map) 
    # Normaliza para o intervalo 0-255
    min_val, max_val = np.min(depth_map), np.max(depth_map)
    if max_val - min_val > 0:
        normalized_depth = 255 * (depth_map - min_val) / (max_val - min_val)
    else:
        normalized_depth = np.zeros_like(depth_map)

    # Converte para uma imagem de 3 canais (RGB) em tons de cinza
    grayscale_image = np.stack([normalized_depth.astype(np.uint8)]*3, axis=-1)
    
    return pygame.surfarray.make_surface(grayscale_image.transpose(1, 0, 2))

def pygame_surface_to_texture(pygame_surface, tex_id):
    """Converte uma superfície Pygame em uma textura OpenGL."""
    rgb_surface = pygame.image.tostring(pygame_surface, 'RGB')
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, pygame_surface.get_width(), pygame_surface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)

def main():
    # Inicializa o Pygame
    pygame.init()
    
    # Define o tamanho da janela
    display = (600, 400)

    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)


    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #Habilita o teste da profundidade 
    glEnable(GL_DEPTH_TEST)
    #escolhe o modo de como passar no test 
    # GL_LESS
    # passa no teste se a proxima profundidade é menor que o armazenado no buffer anterior.
    glDepthFunc(GL_LESS)

    show_zbuffer_view = False 

    pygame.display.set_caption("C3 3D com OpenGL")
    
    # Define a perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, (display[0] / display[1]), 0.1, 50.0)
    
    # Varieveis da camera 
    yaw = 0.0
    pitch = 25.0 
    distance = 25.0

    # controle do mouse 
    mouse_clicado = False

    # Loop principal
    while True:
        # Verifica eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE:
                pygame.quit()
                return
              if event.key == pygame.K_z:
                      show_zbuffer_view = not show_zbuffer_view
                      if show_zbuffer_view:
                          pygame.display.set_caption("Visualização do Z-Buffer (Pressione Z para voltar)")
                      else:
                          pygame.display.set_caption("C3 3D com OpenGL")  
              
            # Eventos para controlar a rotação com clique do mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    mouse_clicado = True
                    pygame.mouse.get_rel()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_clicado = False
            # Evento para controlar o Zoom com a roda do mouse
            elif event.type == pygame.MOUSEWHEEL:
                distance -= event.y * 1.5 # event.y é +1 para cima, -1 para baixo
                if distance < 1.0: distance = 1.0 # Limite mínimo de zoom
                if distance > 80.0: distance = 80.0 # Limite máximo

        if mouse_clicado:
            dx, dy = pygame.mouse.get_rel()
            yaw += dx * 0.5
            pitch -= dy * 0.5
            pitch = np.clip(pitch, -89, 89) # Limita o ângulo vertical  
        

        # limpa o buffer anterior e o buffer da profundidade 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Começa resetando a matriz de ModelView
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # calcula a posição da camera (esfericas cartesianas)
        rad_yaw = np.radians(yaw)
        rad_pitch = np.radians(pitch)

        cam_x = distance * np.cos(rad_pitch) * np.sin(rad_yaw)
        cam_y = distance * np.sin(rad_pitch)
        cam_z = distance * np.cos(rad_pitch) * np.cos(rad_yaw)

        # aplica a tranformação da camera 
        gluLookAt(cam_x, cam_y, cam_z,
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)

        #Cubo central c3
        glPushMatrix()
        glMultMatrixf(scale(4, 6, 3))
        draw_cube()
        glPopMatrix()
        
        #Retangulo maior
        glPushMatrix()
        apply_matrix(scale(12, 4, 3))
        apply_matrix(translate(-0.335, 1.5, 0))
        draw_cube()
        glPopMatrix()
        
        #Cubo da direita - aplicar rotação
        glPushMatrix()
        apply_matrix(scale(4, 4, 3))
        apply_matrix(translate(2, 1.5, 0))
        apply_matrix(rotate_z(np.radians(20)))
        draw_cube()
        glPopMatrix()
        
        #Cubo menor da direita
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(3.7, 2.7, 0))
        apply_matrix(rotate_z(np.radians(20)))
        draw_cube()
        glPopMatrix()
        
        #Cubo da esquerda - aplicar rotação
        glPushMatrix()
        apply_matrix(scale(4, 4, 3))
        apply_matrix(translate(-1, 1.5, 0))
        apply_matrix(rotate_z(np.radians(70)))
        draw_cube()
        glPopMatrix()
        
        #Cubo menor da esquerda
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(-2.35, 2.7, 0))
        apply_matrix(rotate_z(np.radians(70)))
        draw_cube()
        glPopMatrix()
        
        #hexagono do hall
        glPushMatrix()
        apply_matrix(scale(2.5, 2.5, 3))
        apply_matrix(translate(0.78, -0.35, 0))
        draw_hex()
        glPopMatrix()
        
        #Cubo menor do hall - direita
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(-0.18, -1.7, 0))
        apply_matrix(rotate_z(np.radians(45)))
        draw_cube()
        glPopMatrix()
        
        #Cubo menor do hall - esquerda
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(1.48, -0.3, 0))
        apply_matrix(rotate_z(np.radians(-135)))
        draw_cube()
        glPopMatrix()

        if show_zbuffer_view:
           # Se a visualização do z-buffer estiver ativa...
           # 1. Gera a imagem do buffer de profundidade
           depth_surface = visualize_z_buffer(display[0], display[1])
           # 2. Desenha essa imagem na tela, sobrepondo a cena colorida
           #    (Precisamos de um contexto 2D temporário para isso)
           glMatrixMode(GL_PROJECTION)
           glPushMatrix()
           glLoadIdentity()
           gluOrtho2D(0, display[0], 0, display[1])
           glMatrixMode(GL_MODELVIEW)
           glPushMatrix()
           glLoadIdentity()
           # Converte a superfície para uma textura e desenha num retângulo
           tex_id = glGenTextures(1)
           glBindTexture(GL_TEXTURE_2D, tex_id)
           pygame_surface_to_texture(depth_surface, tex_id)
           glEnable(GL_TEXTURE_2D)
           glBegin(GL_QUADS)
           glTexCoord2f(0, 0); glVertex2f(0, 0)
           glTexCoord2f(1, 0); glVertex2f(display[0], 0)
           glTexCoord2f(1, 1); glVertex2f(display[0], display[1])
           glTexCoord2f(0, 1); glVertex2f(0, display[1])
           glEnd()
           glDisable(GL_TEXTURE_2D)
           glDeleteTextures(1, [tex_id])
           # Restaura as matrizes 3D
           glPopMatrix()
           glMatrixMode(GL_PROJECTION)
           glPopMatrix()
           glMatrixMode(GL_MODELVIEW)
    
        # Atualiza a tela
        pygame.display.flip()
        
        # Controla a taxa de quadros
        pygame.time.wait(10)

if __name__ == "__main__":
    main()