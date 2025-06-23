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
    #Calcular t, b, r, l a partir de fovy, aspect, near
    fovy_rad = np.radians(fovy)
    t = near * np.tan(fovy_rad / 2.0)
    b = -t
    r = t * aspect
    l = -r
    n = near
    f = far
    
    #aqui cria uma matriz de zeros e gera a matriz que foi mostrada em sala de aula
    matriz = np.zeros((4, 4), dtype=np.float32)

    matriz[0, 0] = n / r
    matriz[1, 1] = n / t
    matriz[2, 2] = -(f + n) / (f - n)
    matriz[2, 3] = -(2 * f * n) / (f - n)
    matriz[3, 2] = -1.0
    
    return matriz


#funcao que calcula a normal:
def calcular_normal(v0, v1, v2):
    a = np.array(v1) - np.array(v0)
    b = np.array(v2) - np.array(v0)
    normal = np.cross(a, b)
    # Normalizamos o vetor para que ele tenha comprimento 1
    norma = np.linalg.norm(normal)
    # Evita divisão por zero
    if norma == 0:
        return np.array([0.0, 0.0, 1.0]) 
    return normal / norma


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
    
def draw_cube(colors = None):
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
    faces_cubo = [
        (4, 5, 6, 7),  # Topo (Y=1)
        (1, 0, 3, 2),  # Fundo (Y=0)
        (0, 4, 7, 3),  # Esquerda (X=0)
        (5, 1, 2, 6),  # Direita (X=1)
        (7, 6, 2, 3),  # Frente (olhando na direção -Z, se Z aumenta para longe)
        (1, 5, 4, 0)   # Trás (olhando na direção +Z)
    ]

    # Começa a desenhar um polígono
    glBegin(GL_QUADS)
    
    
    # Desenha cada vértice
    for i, face in enumerate(faces_cubo):
        # Pega 3 vértices da face para calcular a normal
        v0 = vertices_cubo[face[0]]
        v1 = vertices_cubo[face[1]]
        v2 = vertices_cubo[face[2]]
        
        #CALCULA E FORNECE A NORMAL
        normal = calcular_normal(v0, v1, v2)
        glNormal3fv(normal)
        # Se uma lista de cores foi passada, define a cor para esta face
        if colors and len(colors) == 6:
            glColor3fv(colors[i])
        
        for vertice_index in face:
            glVertex3fv(vertices_cubo[vertice_index])
    glEnd()
    
def draw_hex():
    radius = 1
    height = 1
    num_lados = 6
    angulos = np.linspace(0, 2 * np.pi, num=num_lados, endpoint=False)

    # Gerar vértices da base e do topo
    base = np.array([[radius * np.cos(a), radius * np.sin(a), 0] for a in angulos])
    topo = base + np.array([0, 0, height])  # mesma base + altura em Z
    # --- Base de baixo ---
    # A normal aponta para "fora" do sólido, então para baixo no eixo Z.
    glNormal3f(0.0, 0.0, -1.0) 
    glBegin(GL_POLYGON)
    # Desenhamos em ordem inversa para que a face "frontal" seja a de baixo.
    for v in reversed(base):
        glVertex3fv(v)
    glEnd()

    # --- Base de cima ---
    # A normal aponta para cima no eixo Z.
    glNormal3f(0.0, 0.0, 1.0)
    glBegin(GL_POLYGON)
    for v in topo:
        glVertex3fv(v)
    glEnd()

    # --- Faces Laterais ---
    glBegin(GL_QUADS)
    for i in range(num_lados):
        v1 = base[i]
        v2 = topo[i]
        v3 = topo[(i + 1) % num_lados]
        v4 = base[(i + 1) % num_lados]
        
        # CALCULA E DEFINE A NORMAL PARA *ESTA* FACE LATERAL
        normal_lateral = calcular_normal(v1, v4, v2)
        glNormal3fv(normal_lateral)
        
        # Agora desenha os vértices da face
        glVertex3fv(v1)
        glVertex3fv(v2)
        glVertex3fv(v3)
        glVertex3fv(v4)
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

def main():
    # Inicializa o Pygame
    pygame.init()
    
    # Define o tamanho da janela
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    # utilizando Z-buffer para a visualização
    glEnable(GL_DEPTH_TEST)
    
    
    # ATIVA ILUMINAÇÃO
    # Habilita o sistema de iluminação
    glEnable(GL_LIGHTING)
    # Liga a primeira fonte de luz
    glEnable(GL_LIGHT0)         
    glEnable(GL_COLOR_MATERIAL)
    
    
    #CONFIGURANDO A LUZ 
    #Luz Ambiente da fonte (luz fraca que preenche a cena)
    luz_ambiente = [0.3, 0.3, 0.3, 1.0] 
    #Luz Difusa da fonte (a cor principal da luz)
    luz_difusa = [0.8, 0.8, 0.8, 1.0] 
    #Luz Especular da fonte (a cor do brilho)
    luz_especular = [1.0, 1.0, 1.0, 1.0]
    #Posição da luz no espaço
    posicao_luz = [5.0, 10.0, 10.0, 1.0]
    
    
    #CONFIGURAR O MATERIAL
    # Define como o material reflete o brilho especular (será branco)
    material_especular = [1.0, 1.0, 1.0, 1.0]
    # Define o quão "polido" é o material (valor alto = brilho pequeno e intenso)
    material_shininess = [50.0]
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    
    
    pygame.display.set_caption("Predio C3")
    
    # Define a perspectiva (só precisa ser chamada uma vez)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


    #Cria a matriz de projeção usando a sua nova função
    fovy = 60
    aspect = display[0] / display[1]
    near = 0.1
    far = 100.0
    proj_mat = perspectiva(fovy, aspect, near, far)
    apply_matrix(proj_mat)        
        
    # Volta para a matriz ModelView para as operações de câmera e objetos
    glMatrixMode(GL_MODELVIEW)

    # --- Variáveis da Câmera  ---
    yaw = 0.0
    pitch = 25.0  # Começa olhando um pouco de cima
    distance = 25.0
    
    # --- Controle do Mouse ---
    mouse_down = False 

    COR_MARROM = (0.5, 0.25, 0.0) # Um marrom (50% vermelho, 25% verde)
    COR_BRANCO = (1.0, 1.0, 1.0) # Branco puro
    #Definindo um vetor pra pintar, ordem: [Topo, Fundo, Esquerda, Direita, Frente, Trás]
    PALETA_MARROM_TETO_BRANCO = [
        COR_BRANCO, # Topo
        COR_BRANCO, # Fundo
        COR_MARROM, # Esquerda
        COR_MARROM, # Direita
        COR_MARROM, # Frente
        COR_MARROM  # Trás
    ]
    # Loop principal
    while True:
        # --- 1. Processamento de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
            # Eventos para controlar a rotação com clique do mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    mouse_down = True
                    pygame.mouse.get_rel()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            # Evento para controlar o Zoom com a roda do mouse
            elif event.type == pygame.MOUSEWHEEL:
                distance -= event.y * 1.5 # event.y é +1 para cima, -1 para baixo
                if distance < 1.0: distance = 1.0 # Limite mínimo de zoom
                if distance > 80.0: distance = 80.0 # Limite máximo

        if mouse_down:
            dx, dy = pygame.mouse.get_rel()
            yaw += dx * 0.5
            pitch -= dy * 0.5
            pitch = np.clip(pitch, -89, 89) # Limita o ângulo vertical

        # --- 2. Limpar a Tela ---
        
        # utilizando Z-buffer para a visualização
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # --- 3. Configurar a Câmera ---
        glLoadIdentity() # Reseta a matriz da câmera a cada quadro

        # Calcula a posição da câmera em uma esfera ao redor da origem
        rad_yaw = np.radians(yaw)
        rad_pitch = np.radians(pitch)

        cam_x = distance * np.cos(rad_pitch) * np.sin(rad_yaw)
        cam_y = distance * np.sin(rad_pitch)
        cam_z = distance * np.cos(rad_pitch) * np.cos(rad_yaw)

        #podemos mudar a ordem do teste da profundidade pelo comando 
        #glDepthFunc(…)
        #por enquanto, não encontramos motivo para mudar. 

        # Aponta a câmera da sua posição calculada para a origem (0,0,0)
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)

        #Cubo central c3
        glPushMatrix()
        glMultMatrixf(scale(4, 6, 3))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        #Retangulo maior
        glPushMatrix()
        apply_matrix(scale(12, 4, 3))
        apply_matrix(translate(-0.335, 1.5, 0))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        #Cubo da direita - aplicar rotação
        glPushMatrix()
        glColor3fv(COR_BRANCO)
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
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        #Cubo da esquerda - aplicar rotação
        glPushMatrix()
        glColor3fv(COR_BRANCO)
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
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        #hexagono do hall
        glPushMatrix()
        glColor3fv(COR_BRANCO)
        apply_matrix(scale(2.5, 2.5, 3))
        apply_matrix(translate(0.78, -0.35, 0.01))
        draw_hex()
        glPopMatrix()
        
        #Cubo menor do hall - direita
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(-0.18, -1.7, 0))
        apply_matrix(rotate_z(np.radians(45)))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        #Cubo menor do hall - esquerda
        glPushMatrix()
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(1.48, -0.3, 0))
        apply_matrix(rotate_z(np.radians(-135)))
        draw_cube(colors=PALETA_MARROM_TETO_BRANCO)
        glPopMatrix()
        
        # --- 5. Atualizar a Tela ---
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()