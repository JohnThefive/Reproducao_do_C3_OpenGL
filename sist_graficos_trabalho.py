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


# Alteração do draw_cube para pegar as vertices e fazer a tonalização (material)     
# Altere a assinatura da função para aceitar os materiais
def draw_cube(material_teto, material_paredes, material_base=None):
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

    # Coordenadas de textura para os 4 cantos de uma face
    tex_coords = [(0,0), (0,1), (1,1), (1,0)]

    # Se nenhum material for fornecido para a base, use o mesmo das paredes
    if material_base is None:
        material_base = material_paredes

    glBegin(GL_QUADS)
    # Usamos enumerate para obter o índice (i) de cada face
    for i, face in enumerate(faces_cubo):
        # Decide qual material aplicar com base no índice da face
        if i == 0: # Índice 0 é o Topo
            apply_material(material_teto)
        elif i == 1: # Índice 1 é a Base
            apply_material(material_base)
        else: # Todas as outras faces são paredes
            apply_material(material_paredes)

        # O cálculo da normal e o desenho dos vértices continua igual
        v0, v1, v2 = vertices_cubo[face[0]], vertices_cubo[face[1]], vertices_cubo[face[2]]
        normal = calcular_normal(v0, v1, v2)
        
        # Usamos enumerate para obter o índice do vértice (0, 1, 2, 3)
        for vert_idx_in_face, vertice_index in enumerate(face):
            glNormal3fv(normal)
            # Usamos o índice do vértice, não o da face
            glTexCoord2f(tex_coords[vert_idx_in_face][0], tex_coords[vert_idx_in_face][1]) 
            glVertex3fv(vertices_cubo[vertice_index])
    glEnd()

# vou mudar a função para suportar o material no hex       
def draw_hex(material_topo, material_laterais, material_base=None):
    radius = 1
    height = 1
    num_lados = 6
    angulos = np.linspace(0, 2 * np.pi, num=num_lados, endpoint=False)

    base = np.array([[radius * np.cos(a), radius * np.sin(a), 0] for a in angulos])
    topo = base + np.array([0, 0, height])
    tex_coords = [(0, 0), (0, 1), (1, 1), (1, 0)] # Coordenadas para os lados
  
    # se eu não definir a cor da base, a cor da base vai ser igual ao material das laterais
    if material_base is None:
        material_base = material_laterais

    # material Base 
    apply_material(material_base)
    glBegin(GL_POLYGON)
    normal_base = [0.0, 0.0, -1.0]
    for v in reversed(base):
        glNormal3fv(normal_base)
        glVertex3fv(v)
    glEnd()    

    # teto 
    apply_material(material_topo)
    glBegin(GL_POLYGON)
    normal_topo = [0.0, 0.0, 1.0]
    for v in topo:
        glNormal3fv(normal_topo)
        glVertex3fv(v)
    glEnd()

    # paredes 
    apply_material(material_laterais)
    glBegin(GL_QUADS)
    for i in range(num_lados):
        v1, v2 = base[i], topo[i]
        v3, v4 = topo[(i + 1) % num_lados], base[(i + 1) % num_lados]
        vertices_face = [v1, v4, v3, v2]
        normal_lateral = calcular_normal(v1, v4, v2)
        
        # Define a normal para cada um dos 4 vértices da face
        # O loop interno agora funciona porque 'vertices_face' existe
        for j, vert in enumerate(vertices_face):
            glNormal3fv(normal_lateral)
            glTexCoord2f(tex_coords[j][0], tex_coords[j][1]) 
            glVertex3fv(vert)
    glEnd()

# quadrado de vidro 
def draw_glass_pane():
    # Vértices de -0.5 a +0.5, para que o centro seja (0,0,0)
    vertices = [
        (-0.5, -0.5, 0.0), # Canto inferior esquerdo
        ( 0.5, -0.5, 0.0), # Canto inferior direito
        ( 0.5,  0.5, 0.0), # Canto superior direito
        (-0.5,  0.5, 0.0)  # Canto superior esquerdo
    ]
    
    # A normal para um plano XY aponta para a direção Z positiva
    normal = [0.0, 0.0, 1.0]

    glBegin(GL_QUADS)
    glNormal3fv(normal)
    for v in vertices:
        glVertex3fv(v)
    glEnd()    

# hexagono de vidro
def  draw_glass_hexagon():
    radius = 1
    num_lados = 6
    angulos = np.linspace(0, 2 * np.pi, num=num_lados, endpoint=False)
    vertices = np.array(
        [[radius * np.cos(a), radius * np.sin(a), 0] for a in angulos],
        dtype=np.float32
    )

    normal = [0.0, 0.0, 1.0]

    glBegin(GL_POLYGON)
    glNormal3fv(normal)
    for v in vertices:
        glVertex3fv(v)
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
def load_texture(filename):
    """
    Carrega uma imagem e a converte em uma textura OpenGL.
    Retorna o ID da textura.
    """
    # Carrega a imagem usando o Pygame
    texture_surface = pygame.image.load(filename)
    
    # Converte a superfície do Pygame para uma string de dados que o OpenGL pode usar
    # O 'True' no final inverte a imagem verticalmente, o que é necessário pois
    # o sistema de coordenadas do Pygame (0,0 no topo-esquerda) é diferente do 
    # sistema de coordenadas de textura do OpenGL (0,0 no canto inferior-esquerdo).
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    # Gera um ID para a nossa textura
    texture_id = glGenTextures(1)

    # Diz ao OpenGL que vamos trabalhar com a textura que acabamos de gerar
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Define como a textura deve se comportar quando é menor ou maior que a área do polígono
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # Define como a textura deve se repetir. GL_REPEAT é perfeito para tijolos.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Envia os dados da imagem (texture_data) para a placa de vídeo
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    return texture_id
# uma função para facilidar a implementação do gl_material as formas.
def apply_material(material):
    glMaterialfv(GL_FRONT, GL_AMBIENT, material["ambient"])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material["diffuse"])
    glMaterialfv(GL_FRONT, GL_SPECULAR, material["specular"])
    glMaterialf(GL_FRONT, GL_SHININESS, material["shininess"])

def main():
    # Inicializa o Pygame
    pygame.init()
    
    # Define o tamanho da janela
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # TIRAR duvida com o professor
    # Ativando o teste de profundidade 
    glEnable(GL_DEPTH_TEST)
    # Escolhendo o modelo de analise de profundidade ( LESS)
    glDepthFunc(GL_LEQUAL)

    #ativando blend e a formula padrão para tranfarencia
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    
    
    # ATIVA ILUMINAÇÃO
    # Habilita o sistema de iluminação
    glEnable(GL_LIGHTING)
    # Liga a primeira fonte de luz
    glEnable(GL_LIGHT0)   

    # remover a influencia de GL_color dos objetos da cena       
    #glEnable(GL_COLOR_MATERIAL)
    #glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)

    # modo de sombreamento para gouraud ( suave)
    glShadeModel(GL_SMOOTH)


    try:
        tijolinhos_texture_id = load_texture("tijolinhos.jpg")
    except pygame.error as e:
        print(f"Erro ao carregar a textura: {e}")
        print("Certifique-se que 'tijolinhos.jpg' está na mesma pasta do script.")
        return
    
    
    
    #CONFIGURANDO A LUZ 
    #Luz Ambiente da fonte (luz fraca que preenche a cena)
    luz_ambiente = [0.3, 0.3, 0.3, 1.0] 
    #Luz Difusa da fonte (a cor principal da luz)
    luz_difusa = [0.8, 0.8, 0.8, 1.0] 
    #Luz Especular da fonte (a cor do brilho)
    luz_especular = [1.0, 1.0, 1.0, 1.0]
    #Posição da luz no espaço
    posicao_luz = [5.0, 10.0, 10.0, 0.0]
    
    
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
    
    # Seleciona a pilha de matriz de projeção
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


    #COR_MARROM = (0.5, 0.25, 0.0) # Um marrom (50% vermelho, 25% verde)
    #COR_BRANCO = (1.0, 1.0, 1.0) # Branco puro
    #Definindo um vetor pra pintar, ordem: [Topo, Fundo, Esquerda, Direita, Frente, Trás]
    #PALETA_MARROM_TETO_BRANCO = [
    #    COR_BRANCO, # Topo
    #    COR_BRANCO, # Fundo
    #    COR_MARROM, # Esquerda
    #    COR_MARROM, # Direita
    #    COR_MARROM, # Frente
    #    COR_MARROM  # Trás
    #]

    #definindo as cores para degrade (teste)
    #COR_BASE_ESCURA = (0.3, 0.15, 0.05) # Um marrom bem escuro
    #COR_TOPO_CLARA = (1, 1, 1)   

    #CORES_DEGRADE_CUBO = [
    #COR_BASE_ESCURA, # Vértice 0 (base)
    #COR_BASE_ESCURA, # Vértice 1 (base)
    #COR_BASE_ESCURA, # Vértice 2 (base)
    #COR_BASE_ESCURA, # Vértice 3 (base)
    #COR_TOPO_CLARA,  # Vértice 4 (topo)
    #COR_TOPO_CLARA,  # Vértice 5 (topo)
    #COR_TOPO_CLARA,  # Vértice 6 (topo)
    #COR_TOPO_CLARA,  # Vértice 7 (topo)
#]
    # Antes definimos as cores atreves de RGB, agora vamos determinar como um material se comporta 
    # interagindo com a luz. 

    MAT_PAREDE_MARROM = {
    "ambient": [0.4, 0.2, 0.1, 1.0], 
    "diffuse": [0.5, 0.25, 0.0, 1.0], 
    "specular": [0.1, 0.1, 0.1, 1.0], 
    "shininess": 10.0                 
    }
    MAT_PAREDE_TEXTURIZADA = {
    "ambient": [0.8, 0.8, 0.8, 1.0],  # Cor ambiente para sombras
    "diffuse": [1.0, 1.0, 1.0, 1.0],  # BRANCO para não tingir a textura
    "specular": [0.1, 0.1, 0.1, 1.0], # Um pouco de brilho
    "shininess": 10.0                 
    }

    # Material para os cubos e hexágonos brancos/cinzas
    MAT_CONCRETO_BRANCO = {
    "ambient": [0.7, 0.7, 0.7, 1.0],
    "diffuse": [0.9, 0.9, 0.9, 1.0], 
    "specular": [1.0, 1.0, 1.0, 1.0], 
    "shininess": 100.0  
    }     

    MAT_VIDRO_AZULADO = {
    "ambient": [0.1, 0.15, 0.2, 0.3],
    "diffuse": [0.2, 0.3, 0.4, 0.3],
    "specular": [1.0, 1.0, 1.0, 1.0],
    "shininess": 120.0
    }  

    MAT_SOLO_PRETO = {
    "ambient": [0.05, 0.05, 0.05, 1.0],
    "diffuse": [0.1, 0.1, 0.1, 1.0],
    "specular": [0.0, 0.0, 0.0, 1.0],
    "shininess": 5.0
    }

     


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
        
        # Limpando a tela de buffer_normal e a tela de buffer da profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # --- 3. Configurar a Câmera ---
        glLoadIdentity() # Reseta a matriz da câmera a cada quadro

        # Calcula a posição da câmera em uma esfera ao redor da origem
        rad_yaw = np.radians(yaw)
        rad_pitch = np.radians(pitch)

        cam_x = distance * np.cos(rad_pitch) * np.sin(rad_yaw)
        cam_y = distance * np.sin(rad_pitch)
        cam_z = distance * np.cos(rad_pitch) * np.cos(rad_yaw)


        # Aponta a câmera da sua posição calculada para a origem (0,0,0)
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)



        #Cubo central c3
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glMultMatrixf(scale(4, 5.5, 4))
        apply_matrix(translate(-0.01, 0.1,0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        #Cubo central c3 - teto
        glPushMatrix()
        glMultMatrixf(scale(3.9, 5.49, 4.1))
        apply_matrix(translate(0, 0.1,0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()
        
        # JANELAS DO CUBO CENTRAL
        
        # 1 janela 
        glPushMatrix()
        apply_matrix(translate(4.01, 3, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 2 janela do meio
        glPushMatrix()
        apply_matrix(translate(4.01, 3, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 3 janela do 1 lado
        glPushMatrix()
        apply_matrix(translate(4.01, 4.5, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 4 janela do 1 lado
        glPushMatrix()
        apply_matrix(translate(4.01, 4.5, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 5 janela 
        glPushMatrix()
        apply_matrix(translate(4.01, 1.5, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 6 janela 
        glPushMatrix()
        apply_matrix(translate(4.01, 1.5, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 7 janela
        glPushMatrix()
        apply_matrix(translate(-0.1, 1.5, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 8 janela 
        glPushMatrix()
        apply_matrix(translate(-0.1, 1.5, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 9 janela 
        glPushMatrix()
        apply_matrix(translate(-0.1, 3, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 10 janela 
        glPushMatrix()
        apply_matrix(translate(-0.1, 3, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 11 janela 
        glPushMatrix()
        apply_matrix(translate(-0.1, 4.5, 0.8))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 12 janela 
        glPushMatrix()
        apply_matrix(translate(-0.1, 4.5, 2.2))
        apply_matrix(rotate_y(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix() 

        #Retangulo maior
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        apply_matrix(scale(12, 4, 4))
        apply_matrix(translate(-0.335, 1.5, 0))
        apply_matrix(translate(0, -0.04, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        #Retangulo maior
        glPushMatrix()
        apply_matrix(scale(11.9, 4, 4.1))
        apply_matrix(translate(-0.335, 1.5, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()
        #Retangulo maior teto
        glPushMatrix()
        apply_matrix(scale(12, 2.0001, 4.50001))
        apply_matrix(translate(-0.335, 4, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_CONCRETO_BRANCO, material_base=MAT_SOLO_PRETO)
        glPopMatrix()
        
        #JANELAS DO RETANGULO MAIOR
        
        # 1 janela 
        glPushMatrix()
        apply_matrix(translate(5.01, 5.99, 2.2))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 2 janela 
        glPushMatrix()
        apply_matrix(translate(5.01, 5.99, 0.8))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 3 janela 
        glPushMatrix()
        apply_matrix(translate(6.5, 5.99, 0.8))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 4  janela 
        glPushMatrix()
        apply_matrix(translate(6.5, 5.99, 2.2))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 5 janela 
        glPushMatrix()
        apply_matrix(translate(-1, 5.99, 2.2))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 6 janela 
        glPushMatrix()
        apply_matrix(translate(-2.5, 5.99, 2.2))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 7 janela 
        glPushMatrix()
        apply_matrix(translate(-2.5, 5.99, 0.8))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # 8 janela 
        glPushMatrix()
        apply_matrix(translate(-1, 5.99, 0.8))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1)) 
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        
                
                
        #Cubo da direita - aplicar rotação (ele é um material agora, e não só uma cor)
        glPushMatrix()
        apply_matrix(scale(4, 4,4))
        apply_matrix(translate(2, 1.5, -0.01))
        apply_matrix(rotate_z(np.radians(20)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()
        #Cubo da direita teto
        glPushMatrix()
        apply_matrix(scale(3.8, 4.2,4.5))
        apply_matrix(translate(2, 1.5, -0.01))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(scale(1, 0.5,1))
        apply_matrix(translate(0.1, 0.7, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()

        # JANELAS DO CUBO DA DIREITA

        # janela 1 
        glPushMatrix()
        apply_matrix(translate(9, 6.3, 0.8))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1.0, 1, 1.0))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        # janela 2
        glPushMatrix()
        apply_matrix(translate(9, 6.3, 2.2))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1.0, 1, 1.0))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        # janela 3
        glPushMatrix()
        apply_matrix(translate(10.5, 6.90, 2.2))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1.0, 1, 1.0))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        # janela 4
        glPushMatrix()
        apply_matrix(translate(10.5, 6.90, 0.8))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1.0, 1, 1.0))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        #Cubo menor da direita
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(3.7, 2.7, 0))
        apply_matrix(rotate_z(np.radians(20)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        #JANELAS PARA O CUBO MENOR DA DIREITA

        #JANELA 1 
        glPushMatrix()
        apply_matrix(translate(12.7, 8.5 , 1.5))
        apply_matrix(rotate_z(np.radians(20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2, 1, 2))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        

        
        #Cubo da esquerda - aplicar rotação
        glPushMatrix()
        glColor3f(0.9, 0.9, 0.9)
        apply_matrix(scale(4, 4, 4))
        apply_matrix(translate(-1, 1.5, -0.01))
        apply_matrix(rotate_z(np.radians(70)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()
        #Cubo da esquerda teto
        glPushMatrix()
        glColor3f(0.9, 0.9, 0.9)
        apply_matrix(scale(4, 4.1, 4.5))
        apply_matrix(translate(-1, 1.5, -0.01))
        apply_matrix(rotate_z(np.radians(70)))
        apply_matrix(scale(0.50001, 1, 1))
        apply_matrix(translate(1, 0, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()

        # VIDROS DO CUBO DA ESQUERDA

        # janela 1 
        glPushMatrix()
        apply_matrix(translate(-5, 6.3, 0.8))
        apply_matrix(rotate_z(np.radians(-20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

         # janela 2
        glPushMatrix()
        apply_matrix(translate(-5, 6.3, 2.2))
        apply_matrix(rotate_z(np.radians(-20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #Janela 3 
        glPushMatrix()
        apply_matrix(translate(-6.5, 6.9, 2.2))
        apply_matrix(rotate_z(np.radians(-20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

         #Janela 4
        glPushMatrix()
        apply_matrix(translate(-6.5, 6.9, 0.8))
        apply_matrix(rotate_z(np.radians(-20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(1, 1, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #Cubo menor da esquerda
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        apply_matrix(scale(3, 3, 3))
        apply_matrix(translate(-2.35, 2.7, 0))
        apply_matrix(rotate_z(np.radians(70)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        # JANELAS DO CUBO MENOR DA ESQUERDA

        #JANELA 1 
        glPushMatrix()
        apply_matrix(translate(-8.7, 8.5 , 1.5))
        apply_matrix(rotate_z(np.radians(-20)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2, 1, 2))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        

        #hexagono do hall
        glPushMatrix()
        apply_matrix(scale(2.5, 2.5, 3.5))
        apply_matrix(translate(0.78, -0.35, 0.01))
        draw_hex(material_topo= MAT_CONCRETO_BRANCO, material_laterais=MAT_CONCRETO_BRANCO, material_base= MAT_SOLO_PRETO)
        glPopMatrix()

        #JANELA DO TOPO DO HEXAGONO

        # Janela do TOPO 
        #JANELA 1 
        glPushMatrix()
        apply_matrix(translate(2.0, -0.9 , 3.55))
        apply_matrix(rotate_z(np.radians(90)))
        apply_matrix(rotate_z(np.radians(-30)))
        apply_matrix(scale(1.2, 1.2, 1.2))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_hexagon()
        glPopMatrix()
        
        #Cubo menor do hall - direita
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        apply_matrix(scale(3.01, 3.01, 4))
        apply_matrix(translate(-0.18, -1.7, 0))
        apply_matrix(rotate_z(np.radians(45)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        #Cubo menor do hall - direita
        glPushMatrix()
        apply_matrix(scale(2.98, 2.98, 4.1))
        apply_matrix(translate(-0.18, -1.7, 0))
        apply_matrix(rotate_z(np.radians(45)))
        apply_matrix(translate(-0.01, -0.01, 0))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()

        #JANELAS DO CUBO MENOR DO HALL - DIREITA

        #Janela 1
        glPushMatrix()
        apply_matrix(translate(-1.8, -2, 2))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(rotate_y(np.radians(45)))
        apply_matrix(scale(0.5, 3.5, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #Janela 2
        glPushMatrix()
        apply_matrix(translate(-1.8, -3.95 , 3))
        apply_matrix(rotate_z(np.radians(-45)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        # janela 3 
        glPushMatrix()
        apply_matrix(translate(-1.8, -3.95 , 1.5))
        apply_matrix(rotate_z(np.radians(-45)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        # Janela 4

        glPushMatrix()
        apply_matrix(translate(0.65, -3.95 , 1.5))
        apply_matrix(rotate_z(np.radians(45)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        # Janela 5 

        glPushMatrix()
        apply_matrix(translate(0.65, -3.95 , 3))
        apply_matrix(rotate_z(np.radians(45)))
        apply_matrix(rotate_x(np.radians(90)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()
        
        #Cubo menor do hall - esquerda
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        apply_matrix(scale(3, 3, 4))
        apply_matrix(translate(1.48, -0.3, 0))
        apply_matrix(rotate_z(np.radians(-135)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        #Cubo menor do hall teto
        glPushMatrix()
        apply_matrix(scale(2.99, 2.99, 4.1))
        apply_matrix(translate(1.48, -0.3, 0))
        apply_matrix(rotate_z(np.radians(-135)))
        draw_cube(material_teto= MAT_CONCRETO_BRANCO, material_paredes=MAT_PAREDE_TEXTURIZADA, material_base=MAT_SOLO_PRETO)
        glPopMatrix()

        # JANELAS MENOR DO HALL - ESQUERDA

        #janela 1 
        glPushMatrix()
        apply_matrix(translate(5.5, -4.1, 3.0))
        apply_matrix(rotate_x(np.radians(-90)))
        apply_matrix(rotate_y(np.radians(-45)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #Janela 2 

        glPushMatrix()
        apply_matrix(translate(5.5, -4.1, 1.5))
        apply_matrix(rotate_x(np.radians(-90)))
        apply_matrix(rotate_y(np.radians(-45)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #Janela 3 
        glPushMatrix()
        apply_matrix(translate(5.5, -1.8, 2))
        apply_matrix(rotate_x(np.radians(-90)))
        apply_matrix(rotate_y(np.radians(-135)))
        apply_matrix(scale(0.5, 3.5, 1))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

        #janela 4 
        glPushMatrix()
        apply_matrix(translate(3.2, -4.0, 1.5))
        apply_matrix(rotate_x(np.radians(-90)))
        apply_matrix(rotate_y(np.radians(-135)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()

         #janela 5
        glPushMatrix()
        apply_matrix(translate(3.2, -4.0, 3.0))
        apply_matrix(rotate_x(np.radians(-90)))
        apply_matrix(rotate_y(np.radians(-135)))
        apply_matrix(scale(2.5, 1, 1.5))
        apply_material(MAT_VIDRO_AZULADO)
        draw_glass_pane()
        glPopMatrix()




        
        # --- 5. Atualizar a Tela ---
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()