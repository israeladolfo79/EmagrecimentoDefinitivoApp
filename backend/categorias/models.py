from django.db import models
from localflavor.br.models import BRCPFField


class DadosPessoais(models.Model):
    class Meta:
        verbose_name_plural = "Dados Pessoais"

    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)
    sexo = models.CharField(max_length=9,choices=[
            ('masculino', "Masculino"),
            ('feminino', "Feminino"),
        ],
        verbose_name="Sexo"
    )
    nascimento = models.DateField(verbose_name="Data de Nascimento (Formato: dia/mês/ano)")
    cpf = BRCPFField("CPF", unique=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a sua altura? (cm)")
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    assistiu_video = models.BooleanField(default=False, verbose_name="Assistiu o video?")

    def __str__(self):
        return self.user

class Doenca(models.Model):
    class Meta:
        verbose_name_plural = "Doenças"
    
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)
    refluxo = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Refluxo?")
    gastrite = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Gastrite?")
    figado = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Problemas no Fígado?")
    renal = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Problemas Renais?")
    tireoide = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Problemas de Tireoide?")
    pressao_alta = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Pressão Alta?")
    diabetes = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Diabetes?")
    colesterol = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você têm Colesterol alto?")
    infos_adicionais = models.TextField(blank=True, null=True,verbose_name="Informe quaisquer doenças ou condições pré-existentes:")

    def __str__(self) -> str:
        return self.user

class Medicamento(models.Model):
    class Meta:
        verbose_name_plural = "Medicamentos"

    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)
    medicamentos = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa medicamentos?")
    medicamentos_utilizados = models.TextField(blank=True, null=True,verbose_name="Caso utilize, informe com suas palavras, o nome do medicamento que você utiliza:")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Cirurgia(models.Model):
    class Meta:
        verbose_name_plural = "Cirurgias"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)      
    cirurgias = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você Já fez alguma cirurgia?")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class ExameSangue(models.Model):
    class Meta:
        verbose_name_plural = "Exames de Sangue"

    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)  
    exame = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você apresentou alteração no exame de sangue?")
    alteracoes = models.TextField(blank=True,null=True,verbose_name="Caso haja alguma, informe as alterações em seu exame de sangue")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Intestino(models.Model):
    class Meta:
        verbose_name_plural = "Intestino"

    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)  
    cor_urina = models.CharField(max_length=30,
    choices=[
            ('transparente', "Transparente"),
            ('amarela_clara', "Amarela Clara"),
            ('amarela_escura', "Amarela Escura"),
        ], 
        verbose_name="Qual a cor da sua urina?")
    fezes = models.CharField(max_length=10,choices=[
            ('ressecadas', "Ressecadas"),
            ('amolecidas', "Amolecidas"),
            ('normais', "Normais"),
        ],
        verbose_name="Qual a consistência das suas fezes?"
    )
    banheiro = models.CharField(max_length=10,choices=[
            ("1 a 2", "1 a 2"),
            ("3 a 4", "3 a 4"),
            ("5 a 7", "5 a 7"),
            ("mais que 7", "Mais que 7"),
        ],
        verbose_name="Quantas vezes você vai ao banheiro por semana?"
    )
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Sono(models.Model):
    class Meta:
        verbose_name_plural = "Sono"

    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False) 
    acorda_noite = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você acorda durante a noite?")
    vezes_acorda_noite = models.IntegerField(verbose_name="Quantas vezes você acorda durante a noite?")
    acorda_noite_banheiro = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você acorda durante a noite para ir ao banheiro?")
    horas_sono = models.CharField(max_length=10,choices=[
            (4, "4 horas"),
            (5, "5 horas"),
            (6, "6 horas"),
            (7, "7 horas"),
            (8, "8 horas"),
            ("Mais que 8", "+ que 8 horas"),
        ],
        verbose_name="Quantas horas você dorme à noite?"
    )
    despertar = models.CharField(max_length=20, 
                                choices=(
                                    ('bem', 'Bem'), 
                                    ('cansado fisicamente', "Cansado Fisicamente"),
                                    ('cansado mentalmente', "Cansado Mentalmente"),
                                    ('cansado ambos', "Cansado Fisico e Mentalmente"),
                                    ),
                                verbose_name="Pela manhã, você acorda:"
                                )
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Alcool(models.Model):
    class Meta:
        verbose_name_plural = "Bebida Alcoólica"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)   
    consome_alcool = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você consome bebida alcoólica?")
    quantidade_vezes = models.IntegerField(verbose_name="Quantas vezes na semana você consome Bebida Alcoólica?")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Suplemento(models.Model):
    class Meta:
        verbose_name_plural = "Suplementos"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)  
    creatina = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Creatina?")
    termogenico = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Termogênico?")
    omega_3 = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Ômega 3?")
    vitamina_d = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Vitamina D?")
    multivitaminico = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Multivitamínico?")
    proteina = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Proteína?")
    maltodextrina = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Você usa Maltodextrina?")
    outros = models.TextField(blank=True,null=True,verbose_name="Se utiliza algum outro suplemento, informe aqui")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class CicloMenstrual(models.Model):
    class Meta:
        verbose_name_plural = "Ciclo Menstrual"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False) 
    quantos_dias_menstrua = models.IntegerField(verbose_name="Por quantos dias você menstrua?")
    quantos_dias_ciclo = models.IntegerField(verbose_name="Quantos dias tem seu ciclo menstrual?")
    ciclo = models.TextField(blank=True,null=True,verbose_name="Seu ciclo é: ")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Antropometricos(models.Model):
    class Meta:
        verbose_name_plural = "Dados Antropométricos"
        
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)
    pescoco = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a medida do seu pescoço? (cm)")
    cintura = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a medida da sua cintura? (cm)")
    quadril = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a medida do seu quadril? (cm)")
    pulso = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a medida do seu pulso? (cm)")
    abdomen = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Qual a medida do seu abdômen? (cm)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Qual seu peso atual? (kg)")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Horarios(models.Model):
    class Meta:
        verbose_name_plural = "Horários"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False)  
    treino = models.TimeField(verbose_name="Qual seu horário de treino?", default='23:25')
    acordar = models.TimeField(verbose_name="Qual seu horário de acordar?")
    cafe_da_manha = models.TimeField(verbose_name="Qual seu horário de café da manhã?")
    lanche_manha = models.TimeField(null=True, blank=True, verbose_name="Qual seu horário de lanche da manhã?")
    almoco = models.TimeField(null=True, blank=True, verbose_name="Qual seu horário de almoço?")
    lanche_tarde_1 = models.TimeField(null=True, blank=True, verbose_name="Qual o horário de seu primeiro lanche da tarde?")
    lanche_tarde_2 = models.TimeField(null=True, blank=True, verbose_name="Qual o horário de seu segundo lanche da tarde?")
    jantar = models.TimeField(null=True, blank=True, verbose_name="Qual seu horário de jantar?")
    dormir = models.TimeField(null=True, blank=True, verbose_name="Qual seu horário de dormir?")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")

    def __str__(self) -> str:
        return self.user

class Exercicios(models.Model):
    class Meta:
        verbose_name_plural = "Exercícios"
    user = models.CharField(max_length=255, verbose_name="Usuário", unique=True, blank=False, null=False) 
    treino = models.CharField(
        max_length=25,
        choices=(
            (0, 'Não Pratico Esportes'),
            (4,'Alongamento'),
            (10, 'Artes Marciais'),
            (5, 'Balé'),
            (8 ,'Basquete Jogo'),
            (6 ,'Basquete Treino'),
            (12 ,'Boxe Luta'),
            (7,'Boxe Treino'),
            (2.5 ,'Caminhada 3.5 km/h'),
            (3 ,'Caminhada 4 km/h'),
            (3.5,'Caminhada 5 km/h'),
            (5,'Caminhada 6.5 km/h'),
            (6.5,'Caminhada 7 km/h'),
            (8,'Caminhada 8 km/h'),
            (4,'Caminhada Lenta'),
            (5,'Caminhada Moderada'),
            (5,'Caminhada na Grama'),
            (3.8,'Caminhada Plano 6 km/h'),
            (6,'Caminhada Subida 6 km/h'),
            (4,'Cliclismo < 16 km/h'),
            (16,'Cliclismo > 32 km/h'),
            (6,'Cliclismo a 16 - 19km/h'),
            (8,'Cliclismo a 19.3 - 22.3km/h'),
            (10,'Cliclismo a 22.5 - 25.5 km/h'),
            (12,'Cliclismo a 25.7 - 30.5 km/h'),
            (8,'Corda, Pular Lento'),
            (10,'Corda, Pular Moderado'),
            (12,'Corda, Pular Rápido'),
            (11.5,'Corrida a 10,5km/h'),
            (11,'Corrida a 10km/h'),
            (12.5,'Corrida a 11,2km/h'),
            (14,'Corrida a 12,9km/h'),
            (13.5,'Corrida a 12km/h'),
            (15,'Corrida a 13,5km/h'),
            (16,'Corrida a 15km/h'),
            (18,'Corrida a 16,3km/h'),
            (8,'Corrida a 7,5km/h'),
            (9,'Corrida a 7,8km/h'),
            (10,'Corrida a 9km/h'),
            (10,'Cross Fit Avançado'),
            (8,'Cross Fit Inciante'),
            (7,'Dança Alto Impacto'),
            (5,'Dança baixo Impacto'),
            (5.5,'Dança de Salão'),
            (15,'Escadas Ritmo Acelerado(Simulador)'),
            (8,'Escadas Ritmo Lento (Simulador)'),
            (10,'Escadas Ritmo Médio (Simulador)'),
            (10,'Escalada'),
            (8.5,'Funcional'),
            (10,'Futebol Americano'),
            (10,'Futebol Competitivo'),
            (7,'Futebol Recreativo'),
            (9,'Handebol'),
            (4,'Hidroginastica'),
            (5,'Jazz'),
            (5,'Musculação Hipertrofia'),
            (3.5,'Musculação Resistência'),
            (11,'Natação Boboleta'),
            (7,'Natação Costas'),
            (8,'Natação Craw 3 km/h'),
            (11,'Natação Craw 4 km/h'),
            (6,'Natação Lazer'),
            (7,'Natação Livre Moderada/Leve'),
            (10,'Natação Livre Vigorosa'),
            (6,'Natação no Mar'),
            (10,'Natação Peito'),
            (12,'Patinação'),
            (10,'Polo Aquático'),
            (10,'Rugbi'),
            (5,'Skate'),
            (12,'Squash'),
            (8.5,'Step 15 a 20 centímetros'),
            (10,'Step 21 a 30 centímetros'),
            (10,'Tenis Jogador Avançado'),
            (6,'Tenis Jogador Iniciante'),
            (8,'Tenis Jogador Intermediário'),
            (5,'Tenis treino'),
            (7,'Tennis'),
            (5,'Tennis Dupla'),
            (8,'Treino em Circuito'),
            (9,'Trotar'),
            (8,'Volei Competitivo'),
            (8,'Volei Praia'),
            (4,'Volei Recreativo'),
            (4,'Yoga'),
            (6.5,'Zumba'),

        ),
         verbose_name="Qual exercício você pratica?",)
    tempo_exercicio = models.IntegerField(verbose_name="Tempo de exercício (Minutos)",default=0,)
    treino_secundario = models.CharField(
        max_length=25,
        default=0,
        choices=(
            (0, 'Não Pratico Esportes'),
            (4,'Alongamento'),
            (10, 'Artes Marciais'),
            (5, 'Balé'),
            (8 ,'Basquete Jogo'),
            (6 ,'Basquete Treino'),
            (12 ,'Boxe Luta'),
            (7,'Boxe Treino'),
            (2.5 ,'Caminhada 3.5 km/h'),
            (3 ,'Caminhada 4 km/h'),
            (3.5,'Caminhada 5 km/h'),
            (5,'Caminhada 6.5 km/h'),
            (6.5,'Caminhada 7 km/h'),
            (8,'Caminhada 8 km/h'),
            (4,'Caminhada Lenta'),
            (5,'Caminhada Moderada'),
            (5,'Caminhada na Grama'),
            (3.8,'Caminhada Plano 6 km/h'),
            (6,'Caminhada Subida 6 km/h'),
            (4,'Cliclismo < 16 km/h'),
            (16,'Cliclismo > 32 km/h'),
            (6,'Cliclismo a 16 - 19km/h'),
            (8,'Cliclismo a 19.3 - 22.3km/h'),
            (10,'Cliclismo a 22.5 - 25.5 km/h'),
            (12,'Cliclismo a 25.7 - 30.5 km/h'),
            (8,'Corda, Pular Lento'),
            (10,'Corda, Pular Moderado'),
            (12,'Corda, Pular Rápido'),
            (11.5,'Corrida a 10,5km/h'),
            (11,'Corrida a 10km/h'),
            (12.5,'Corrida a 11,2km/h'),
            (14,'Corrida a 12,9km/h'),
            (13.5,'Corrida a 12km/h'),
            (15,'Corrida a 13,5km/h'),
            (16,'Corrida a 15km/h'),
            (18,'Corrida a 16,3km/h'),
            (8,'Corrida a 7,5km/h'),
            (9,'Corrida a 7,8km/h'),
            (10,'Corrida a 9km/h'),
            (10,'Cross Fit Avançado'),
            (8,'Cross Fit Inciante'),
            (7,'Dança Alto Impacto'),
            (5,'Dança baixo Impacto'),
            (5.5,'Dança de Salão'),
            (15,'Escadas Ritmo Acelerado(Simulador)'),
            (8,'Escadas Ritmo Lento (Simulador)'),
            (10,'Escadas Ritmo Médio (Simulador)'),
            (10,'Escalada'),
            (8.5,'Funcional'),
            (10,'Futebol Americano'),
            (10,'Futebol Competitivo'),
            (7,'Futebol Recreativo'),
            (9,'Handebol'),
            (4,'Hidroginastica'),
            (5,'Jazz'),
            (5,'Musculação Hipertrofia'),
            (3.5,'Musculação Resistência'),
            (11,'Natação Boboleta'),
            (7,'Natação Costas'),
            (8,'Natação Craw 3 km/h'),
            (11,'Natação Craw 4 km/h'),
            (6,'Natação Lazer'),
            (7,'Natação Livre Moderada/Leve'),
            (10,'Natação Livre Vigorosa'),
            (6,'Natação no Mar'),
            (10,'Natação Peito'),
            (12,'Patinação'),
            (10,'Polo Aquático'),
            (10,'Rugbi'),
            (5,'Skate'),
            (12,'Squash'),
            (8.5,'Step 15 a 20 centímetros'),
            (10,'Step 21 a 30 centímetros'),
            (10,'Tenis Jogador Avançado'),
            (6,'Tenis Jogador Iniciante'),
            (8,'Tenis Jogador Intermediário'),
            (5,'Tenis treino'),
            (7,'Tennis'),
            (5,'Tennis Dupla'),
            (8,'Treino em Circuito'),
            (9,'Trotar'),
            (8,'Volei Competitivo'),
            (8,'Volei Praia'),
            (4,'Volei Recreativo'),
            (4,'Yoga'),
            (6.5,'Zumba'),

        ),
         verbose_name="Insira seu segundo treino")
    tempo_exercicio_secundario = models.IntegerField(default=0,verbose_name="Tempo de exercício Secundário (Minutos)")
    infos_adicionais = models.TextField(blank=True,null=True,verbose_name="Se julgar necessário informar algo, utilize este campo")
    def __str__(self) -> str:
        return self.user
