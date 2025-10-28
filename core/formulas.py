from . import models
from datetime import datetime, date
from django.shortcuts import redirect

def parte_a(peso, abdomen, pulso, sexo, quadril, altura):
    c_1 = float(1.038786)*float(peso)
    c_2 = (float(abdomen)-float(pulso))
    c_3 = 0.82816 * float(c_2)
    if sexo == "masculino":
        parte_a = 41.955+(c_1)-(c_3)
    else:
        parte_a = ((0.55*float(quadril))-(0.24*float(altura))+(0.28*float(abdomen))-8.43)
    return parte_a

def gordura_atual(peso, parte_a, sexo):
    if sexo == "masculino":
        g_atual = (((float(peso) - float(parte_a))*100)/float(peso))
    else:
        g_atual = parte_a
    return g_atual

def gordura_ideal(sexo, idade) -> int:
    if sexo == "masculino":
        if idade >= 18 and idade <= 25:
            gordura_ideal = 15
        elif idade >= 26 and idade <= 35:
            gordura_ideal = 19
        elif idade >= 36 and idade <= 45:
            gordura_ideal = 21
        else:
            gordura_ideal = 24
    else:
        if idade >= 18 and idade <= 25:
            gordura_ideal = 23
        elif idade >= 26 and idade <= 35:
            gordura_ideal = 25
        elif idade >= 36 and idade <= 45:
            gordura_ideal = 27
        elif idade >= 46 and idade <= 55:
            gordura_ideal = 29
        else:
            gordura_ideal = 30
    return gordura_ideal

def gordura_meta(gordura_ideal, gordura_atual, sexo):
    ga = round(float(gordura_atual), 1)
    gi = round(float(gordura_ideal), 1)
    if sexo == "masculino":
        if ga > 15:
            if ga <= (gi+5):
                gm = 10
            else:
                gm = gi
        else:
            gm = 8
    else:
        if ga <= (gi+5):
            gm = 16
        else:
            gm = gi
    return gm
    
def gordura_perfeita(sexo, idade) -> int:
    if sexo == "masculino":
        if idade >= 18 and idade <= 25:
            gordura_ideal = 8
        elif idade >= 26 and idade <= 35:
            gordura_ideal = 12
        elif idade >= 35 and idade <= 46:
            gordura_ideal = 16
        elif 46 < idade <= 55:
            gordura_ideal = 18
        else:
            gordura_ideal = 20
    else:
        if idade >= 18 and idade <= 25:
            gordura_ideal = 17
        elif idade >= 26 and idade <= 35:
            gordura_ideal = 18
        elif idade >= 36 and idade <= 45:
            gordura_ideal = 20
        elif idade >= 46 and idade <= 55:
            gordura_ideal = 23
        else:
            gordura_ideal = 24
    return gordura_ideal


def gera_estado_e_per_gordura(percentual_gordura_atual=0, idade=0, sexo="masculino"):
    pga = int(percentual_gordura_atual)

    if pga < 0 or pga > 100:
        return "Valor inválido", "Valor inválido"

    tabela = {
        'excelente': ["ABAIXO DA MÉDIA", "EXCELENTE"],
        'muito_bom': ["ABAIXO DA MÉDIA", "MUITO BOM"],
        'bom': ["ABAIXO DA MÉDIA", "BOM"],
        'normal': ["NA MÉDIA", "NORMAL"],
        'regular': ["ACIMA DA MÉDIA", "REGULAR"],
        'ruim': ["ACIMA DA MÉDIA", "RUIM"],
        'muito_ruim': ["ACIMA DA MÉDIA", "MUITO RUIM"],
    }

    #  FAIXAS MASCULINAS
    if sexo == "masculino":
        if 18 <= idade <= 25:
            dici = {
                tuple(range(0, 7)): 'excelente',        # <= 6%
                tuple(range(7, 11)): 'muito_bom',       # 7-10
                tuple(range(11, 14)): 'bom',            # 11-13
                tuple(range(14, 17)): 'normal',         # 14-16
                tuple(range(17, 21)): 'regular',        # 17-20
                tuple(range(21, 26)): 'ruim',           # 21-25
                tuple(range(26, 101)): 'muito_ruim'     # 26-100
            }

        elif 26 <= idade <= 35:
            dici = {
                tuple(range(0, 12)): 'excelente',       # 8-11
                tuple(range(12, 16)): 'muito_bom',      # 12-15
                tuple(range(16, 19)): 'bom',            # 16-18
                tuple(range(19, 21)): 'normal',         # 19-20
                tuple(range(21, 25)): 'regular',        # 21-24
                tuple(range(25, 28)): 'ruim',           # 25-27
                tuple(range(28, 101)): 'muito_ruim'     # 28-100
            }

        elif 36 <= idade <= 45:
            dici = {
                tuple(range(0, 15)): 'excelente',      # 10-14
                tuple(range(15, 19)): 'muito_bom',      # 15-18
                tuple(range(19, 21)): 'bom',            # 19-20
                tuple(range(21, 24)): 'normal',         # 21-23
                tuple(range(24, 28)): 'regular',        # 24-27
                tuple(range(28, 31)): 'ruim',           # 28-30
                tuple(range(31, 101)): 'muito_ruim'     # 31-100
            }

        else:  # 46+
            dici = {
                tuple(range(0, 14)): 'excelente',       # 4-11
                tuple(range(14, 17)): 'muito_bom',      # 12-16
                tuple(range(17, 21)): 'bom',            # 17-20
                tuple(range(21, 24)): 'normal',         # 21-23
                tuple(range(24, 28)): 'regular',        # 24-27
                tuple(range(28, 31)): 'ruim',           # 28-30
                tuple(range(31, 101)): 'muito_ruim'     # 31-100
            }

    #  FAIXAS FEMININAS
    else:
        if 18 <= idade <= 25:
            dici = {
                tuple(range(0, 17)): 'excelente',      # 13-16
                tuple(range(17, 20)): 'muito_bom',      # 17-19
                tuple(range(20, 23)): 'bom',            # 20-22
                tuple(range(23, 26)): 'normal',         # 23-25
                tuple(range(26, 29)): 'regular',        # 26-28
                tuple(range(29, 32)): 'ruim',           # 29-31
                tuple(range(32, 101)): 'muito_ruim'     # 32-100
            }

        elif 26 <= idade <= 35:
            dici = {
                tuple(range(0, 18)): 'excelente',
                tuple(range(18, 21)): 'muito_bom',
                tuple(range(21, 24)): 'bom',
                tuple(range(24, 26)): 'normal',
                tuple(range(26, 30)): 'regular',
                tuple(range(30, 34)): 'ruim',
                tuple(range(34, 101)): 'muito_ruim'
            }

        elif 36 <= idade <= 45:
            dici = {
                tuple(range(0, 20)): 'excelente',
                tuple(range(20, 24)): 'muito_bom',
                tuple(range(24, 27)): 'bom',
                tuple(range(27, 30)): 'normal',
                tuple(range(30, 33)): 'regular',
                tuple(range(33, 37)): 'ruim',
                tuple(range(37, 101)): 'muito_ruim'
            }

        else:  # 46+
            dici = {
                tuple(range(0, 22)): 'excelente',
                tuple(range(22, 26)): 'muito_bom',
                tuple(range(26, 29)): 'bom',
                tuple(range(29, 32)): 'normal',
                tuple(range(32, 35)): 'regular',
                tuple(range(35, 39)): 'ruim',
                tuple(range(39, 101)): 'muito_ruim'
            }

    # Localiza classificação do PERCENTUAL
    classificacao = next(
        (v for k, v in dici.items() if pga in k),
        'muito_ruim'
    )

    estado, posicao = tabela[classificacao]
    return estado, posicao











# # #esta função deve pegar o percentual de gordura atual e o range do gordura ideal e definir qual o estado
# def gera_estado_e_per_gordura(percentual_gordura_atual, idade, sexo):
#     pga = int(percentual_gordura_atual) #pegando o inteiro do percentual de gordura atual
#     if pga < 0 or pga > 100:
#         estado = "Valor inválido"
#         per_gordura = "Valor inválido"
#         return estado, per_gordura
#     tabela = {
#         'excelente': ["ABAIXO DA MÉDIA", 'EXCELENTE'],
#         'muito_bom': ["ABAIXO DA MÉDIA", 'MUITO BOM'],
#         'bom': ["ABAIXO DA MÉDIA", 'BOM'],
#         'normal': ["NA MÉDIA", 'NORMAL'],
#         'regular': ["ACIMA DA MÉDIA", 'REGULAR'],
#         'ruim': ["ACIMA DA MÉDIA", 'RUIM'],
#         'muito_ruim': ["ACIMA DA MÉDIA", 'MUITO RUIM'],
#     }
#     if sexo == "masculino":
#         if idade >= 18 and idade <= 25:
#             dici = {
#                 f'{[4, 5, 6]}': 'excelente',
#                 f'{[7, 8, 9, 10]}': 'muito_bom',
#                 f'{[11, 12, 13]}': 'bom',
#                 f'{[14, 15, 16]}': 'normal',
#                 f'{[17, 18, 19, 20]}': 'regular',
#                 f'{[21, 22, 23, 24, 25]}': 'ruim',
#                 f'{[i for i in range(26, 100)]}': 'muito_ruim'
#             } 
#         elif idade >= 26 and idade <= 35:
#             dici = {
#                 f'{[8, 9, 10, 11]}': 'excelente',
#                 f'{[12, 13, 14, 15]}': 'muito_bom',
#                 f'{[16, 17, 18]}': 'bom',
#                 f'{[19, 20]}': 'normal',
#                 f'{[21, 22, 23, 24]}': 'regular',
#                 f'{[25, 26, 27]}': 'ruim',
#                 f'{[i for i in range(28, 100)]}': 'muito_ruim'
#             } 
#         elif idade >= 36 and idade <= 45:
#             dici = {
#                 f'{[10, 11, 12, 13, 14]}': 'excelente',
#                 f'{[15, 16, 17, 18]}': 'muito_bom',
#                 f'{[19, 20]}': 'bom',
#                 f'{[21, 22, 23]}': 'normal',
#                 f'{[24, 25, 26, 27]}': 'regular',
#                 f'{[28, 29, 30]}': 'ruim',
#                 f'{[i for i in range(31, 100)]}': 'muito_ruim'
#             } 
#         else:
#             dici = {
#                 f'{[12, 13, 14, 15, 16]}': 'excelente',
#                 f'{[17, 18, 19, 20]}': 'muito_bom',
#                 f'{[21, 22, 23]}': 'bom',
#                 f'{[24, 25, 23]}': 'normal',
#                 f'{[26, 27, 28]}': 'regular',
#                 f'{[29, 30, 31]}': 'ruim',
#                 f'{[i for i in range(32, 100)]}': 'muito_ruim'
#             } 
#     else:
#         if idade >= 18 and idade <= 25:
#                 dici = {
#                     f'{[13, 14, 15, 16]}': 'excelente',
#                     f'{[17, 18, 19]}': 'muito_bom',
#                     f'{[20, 21, 22]}': 'bom',
#                     f'{[23, 24, 25]}': 'normal',
#                     f'{[26, 27, 28]}': 'regular',
#                     f'{[29, 30, 31]}': 'ruim',
#                     f'{[i for i in range(32, 100)]}': 'muito_ruim'
#                 } 
#         elif idade >= 26 and idade <= 35:
#             dici = {
#                 f'{[14, 15, 16, 17]}': 'excelente',
#                 f'{[18, 19, 20]}': 'muito_bom',
#                 f'{[21, 22, 23]}': 'bom',
#                 f'{[24, 25]}': 'normal',
#                 f'{[26, 27, 28, 29]}': 'regular',
#                 f'{[30, 31, 32, 33]}': 'ruim',
#                 f'{[i for i in range(34, 100)]}': 'muito_ruim'
#             } 
#         elif idade >= 36 and idade <= 45:
#             dici = {
#                 f'{[16, 17, 18, 19]}': 'excelente',
#                 f'{[20, 21, 22, 23]}': 'muito_bom',
#                 f'{[24, 25, 26]}': 'bom',
#                 f'{[27, 28, 29]}': 'normal',
#                 f'{[30, 31, 32]}': 'regular',
#                 f'{[33, 34, 35, 36]}': 'ruim',
#                 f'{[i for i in range(37, 100)]}': 'muito_ruim'
#             } 
#         else:
#             dici = {
#             f'{[17, 18, 19, 20, 21]}': 'excelente',
#             f'{[22, 23, 24, 25]}': 'muito_bom',
#             f'{[26, 27, 28]}': 'bom',
#             f'{[29, 30, 31]}': 'normal',
#             f'{[32, 33, 34]}': 'regular',
#             f'{[35, 36, 37, 38]}': 'ruim',
#             f'{[i for i in range(39, 100)]}': 'muito_ruim'
#         } 

#     for key, value in dici.items():
#         if str(pga) in key:
#             classificacao = value
#     clas = tabela[classificacao]
#     return clas[0], clas[1]




def peso_ajustado(peso, percentual_gordura_atual, percentual_gordura_ideal):
    peso_gordura_atual = (peso/100)*percentual_gordura_atual
    peso_massa_magra_atual = peso - peso_gordura_atual
    peso_gordura_ideal = (percentual_gordura_ideal * peso_massa_magra_atual) / (100-percentual_gordura_ideal)
    pa = ((peso_gordura_atual - peso_gordura_ideal)/4) + peso_gordura_ideal + peso_massa_magra_atual
    return pa
    

def calorias_sem_treino(sexo, altura,peso, pa, idade, variavel_1=6.0033, variavel_2=13.7516, variavel_3=6.755, variavel_4=2.8496, variavel_5=9.5634, variavel_6=4.6756):
    if sexo == "masculino":
        cal_sem_treino = ((66.437+(variavel_1*altura))+(variavel_2*pa))-variavel_3*idade
    else:
        cal_sem_treino = ((655.0955+(variavel_4*altura))+(variavel_5*pa))-variavel_6*idade
    return cal_sem_treino

def calorias_com_treino(cal_sem_treino, n_atividade, pa, tempo_atividade):
    cal_com_treino = cal_sem_treino + (n_atividade*pa)/60*tempo_atividade
    return cal_com_treino

def cal_com_treino_duplo(cal_com_treino, n_atividade_2,pa, tempo_atividade_2):
    cal_com_dois_treinos = cal_com_treino + (n_atividade_2*pa)/60*tempo_atividade_2
    return cal_com_dois_treinos

def cintura_quadril(sexo, idade, quadril, cintura):
    rel = round(float(cintura)/ float(quadril), 2)
    if idade <= 29:
        if sexo == "masculino":
            if rel < 0.83:
                v = "NO"
            elif 0.830 <= rel <= 0.940:
                v = "AU"
            else:
                v = "MA"
        else:
            if rel < 0.71:
                v = "NO"
            elif 0.71 <= rel <= 0.820:
                v = "AU"
            else:
                v = "MA"

    elif idade <= 39:
        if sexo == "masculino":
            if rel < 0.84:
                v = "NO"
            elif  0.84 <= rel <= 0.960:
                v = "AU"
            else:
                v = "MA"
        else:
            if rel < 0.72:
                v = "NO"
            elif 0.72 <= rel <= 0.84:
                v = "AU"
            else:
                v = "MA"

    elif idade <= 49:
        if sexo == "masculino":
            if rel < 0.88:
                v = "NO"
            elif 0.880 <= rel <= 1:
                v = "AU"
            else:
                v = "MA"
        else:
            if rel < 0.73:
                v = "NO"
            elif 0.73 <= rel <= 0.87:
                v = "AU"
            else:
                v = "MA"

    elif idade <= 59:
        if sexo == "masculino":
            if rel < 0.90:
                v = "NO"
            elif 0.90 <= rel <= 1.02:
                v = "AU"
            else:
                v = "MA"
        else:
            if rel < 0.74:
                v = "NO"
            elif 0.74 <= rel <= 0.88:
                v = "AU"
            else:
                v = "MA"

    elif idade < 69:
        if sexo == "masculino":
            if rel < 0.91:
                v = "NO"
            elif 0.91 <= rel <= 103:
                v = "AU"
            else:
                v = "MA"
        else:
            if rel < 0.76:
                v = "NO"
            elif 0.76 <= rel <= 0.90:
                v = "AU"
            else:
                v = "MA"
    return v
        
def calcula_abdomen(sexo, circunferencia_abdomen):
    if sexo == "masculino" :
        if circunferencia_abdomen < 94:
           return "NO"
        elif 94 <= circunferencia_abdomen <= 101:
            return "AU"
        else:
            return "MA"
    else:
        if circunferencia_abdomen <= 80:
           return "NO"
        elif 80 < circunferencia_abdomen < 88:
            return "AU"
        else:
            return "MA"

def calcula_cintura(altura, cintura):
    if cintura < (altura/2):
        return "NO"
    else:
        return "AU"

def calcula_quadril(sexo, quadril, altura):
    altura = round(float(altura)/ 100, 2)
    value = int(quadril / (altura * (altura ** 0.5))) - 18
    if sexo == "masculino":
        if value <= 20:
            v = "NO" 
        elif value <= 25:
            v = "AU" 
        else:
            v = "MA" 
    else:
        if value <= 32:
            v = "NO" 
        elif value <= 38:
            v = "AU" 
        else:
            v = "MA" 
    return v

#esta função verifica se o usuário possui dias restantes de acesso ao sistema
def verifica_usuario(username):

    #pega a data atual
    hoje = date.today()
    dat = models.Usuario.objects.get(usuario=username).dias_restantes
    try:
        int(dat)
        qs = datetime.now().date()
    except ValueError:
        try:
            qs = datetime.strptime(dat, "%d/%m/%Y").date()
        except ValueError:
            qs = datetime.now().date()
    calculo = (qs - hoje).days
    if calculo < 0:
        # não possui dias restantes
        return False
    else:
        # possui dias restantes
        return True

#essa função verifica se faz mais que 7 dias que o usuário realizou o primeiro plano alimentar
def verifica_plano_alimentar(username):
    data_plano = list(models.PlanoAlimentar.objects.filter(user=username).order_by("data_realizacao").values())[0]["data_realizacao"]
    hoje = date.today()
    calculo = (hoje - data_plano).days
    if calculo >= 7:
        # plano a mais de 7 dias
        return True
    else:
        # plano a menos de 7 dias
        return False
