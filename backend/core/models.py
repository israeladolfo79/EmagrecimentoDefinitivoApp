from email.policy import default
from tabnanny import verbose
from django.db import models
from categorias import models as categorias_models
from academias.models import Academia

class PaginaInicial(models.Model):
    class Meta:
        verbose_name_plural = "Pagina Inicial"   
    mensagem_1 = models.TextField(verbose_name="Mensagem 1", blank=True, null= True)
    mensagem_2 = models.TextField(verbose_name="Mensagem 2", blank=True, null= True)
    mensagem_3 = models.TextField(verbose_name="Mensagem 3", blank=True, null= True)
    mensagem_4 = models.TextField(verbose_name="Mensagem 4", blank=True, null= True)
    
class DashBoard(models.Model):
    titulo_1 = models.CharField(max_length=255, verbose_name="Título 1")
    subtitulo_1 = models.CharField(max_length=255, verbose_name="Subtítulo 1")
    texto_1 = models.TextField(verbose_name="Texto 1")
    texto_2 = models.TextField(verbose_name="Texto 2")
    texto_3 = models.TextField(verbose_name="Texto 3")
    titulo_2 = models.CharField(max_length=255, verbose_name="Título 2")
    subtitulo_2 = models.CharField(max_length=255, verbose_name="Subtítulo 2")
    link_video = models.CharField(max_length=255, verbose_name="Link para o Video")
    tamanho_titulo =  models.CharField(
        max_length=3, 
        choices=(
            ('t22', "Tamanho 22"),
            ('t24', "Tamanho 24"),
            ('t26', "Tamanho 26"),
            ('t28', "Tamanho 28"),
            ('t30', "Tamanho 30"),
            ('t35', "Tamanho 35"),
            ('t40', "Tamanho 40")
        ),
        default="t30",
        verbose_name="Tamanho do título"
    )
    tamanho_subtitulo = models.CharField(
        max_length=3, 
        choices=(
            ('t18', "Tamanho 18"),
            ('t20', "Tamanho 20"),
            ('t22', "Tamanho 22"),
            ('t24', "Tamanho 24"),
            ('t26', "Tamanho 26")
        ),
        default="t24",
        verbose_name="Tamanho do subtítulo"
    )
    tamanho_texto =  models.CharField(
        max_length=3, 
        choices=(
            ('t14', "Tamanho 14"),
            ('t16', "Tamanho 16"),
            ('t18', "Tamanho 18"),
            ('t20', "Tamanho 20"),
            ('t22', "Tamanho 22")
        ),
        default="t14",
        verbose_name="Tamanho do texto"
    )

class PlanoAlimentar(models.Model):
    user = models.CharField(max_length=255, verbose_name="Usuário")
    pescoco = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Pescoço (cm)")
    cintura = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Cintura (cm)")
    quadril = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Quadril (cm)")
    pulso = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Pulso (cm)")
    abdomen = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Abdômen (cm)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (kg)")
    percentual_gordura = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Percentual de Gordura")
    gordura_corporal = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Gordura Corporal")
    treino = models.CharField(max_length=20, choices=(('s', 'Sim'), ('n', "Não")),verbose_name="Treino")
    horario_treino = models.TimeField(verbose_name="Horário de Treino")
    café_da_manha = models.TimeField(verbose_name="Horário do café da manhã")
    almoco = models.TimeField(null=True, blank=True,verbose_name="Horário do almoço")
    lanche_1 = models.TimeField(null=True, blank=True,verbose_name="Lanche_1")
    lanche_2 = models.TimeField(null=True, blank=True,verbose_name="Lanche_2")
    lanche_3 = models.TimeField(null=True, blank=True,verbose_name="Lanche_3")
    horario_janta = models.TimeField(null=True, blank=True,verbose_name="Horário de Janta")
    
    data_realizacao = models.DateField(verbose_name="Data de realização da avaliação")
    kcal = models.IntegerField(verbose_name="Kcal Com Treino")
    kcal_simples = models.IntegerField(verbose_name="Kcal Sem Treino", default=True, null=True)

class Usuario(models.Model):
    usuario = models.CharField(max_length=255, verbose_name="Usuário", primary_key=True)
    nome = models.CharField(max_length=255, verbose_name="Nome")
    sobrenome = models.CharField(max_length=255, verbose_name="Sobrenome")
    email = models.EmailField(verbose_name='Email', unique=True)
    senha = models.CharField(max_length=255, verbose_name="Senha")
    repetir_senha = models.CharField(max_length=255,verbose_name="Insira a Senha Novamente")
    avaliacoes = models.IntegerField(verbose_name="Avaliações restantes", default=0)
    tipo_plano = models.IntegerField(verbose_name="Pacote contratado", default=0)
    dias_restantes = models.CharField(max_length=255, verbose_name="Dias de acesso", default="")
    assistiu_video = models.BooleanField(verbose_name="Assistiu o Vídeo",default=False)
    academia = models.ForeignKey(Academia, on_delete=models.DO_NOTHING, verbose_name="Academia", default=9999999999999999)
    
    dados_pessoais = models.OneToOneField(
        categorias_models.DadosPessoais,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    doencas = models.OneToOneField(
        categorias_models.Doenca,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    medicamentos = models.OneToOneField(
        categorias_models.Medicamento,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    cirurgias = models.OneToOneField(
        categorias_models.Cirurgia,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    exame_sangue = models.OneToOneField(
        categorias_models.ExameSangue,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    intestino = models.OneToOneField(
        categorias_models.Intestino,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    sono = models.OneToOneField(
        categorias_models.Sono,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    alcool = models.OneToOneField(
        categorias_models.Alcool,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    suplementos = models.OneToOneField(
        categorias_models.Suplemento,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    ciclo_menstrual = models.OneToOneField(
        categorias_models.CicloMenstrual,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    dados_atropometricos = models.OneToOneField(
        categorias_models.Antropometricos,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    horarios = models.OneToOneField(
        categorias_models.Horarios,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    exercicios = models.OneToOneField(
        categorias_models.Exercicios,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.usuario

class Variaveis(models.Model):
    class Meta:
        verbose_name_plural = "Variáveis"
    var_1 = models.FloatField(verbose_name='Variável 1')
    var_2 = models.FloatField(verbose_name='Variável 2')
    var_3 = models.FloatField(verbose_name='Variável 3')
    var_4 = models.FloatField(verbose_name='Variável 4')
    var_5 = models.FloatField(verbose_name='Variável 5')
    var_6 = models.FloatField(verbose_name='Variável 6')

class CategoriaMaterialDeApoio(models.Model):
    class Meta:
        verbose_name_plural = "Categorias De Materiais"
    nome = models.CharField(max_length=255, verbose_name="Nome da Categoria")
    palavras_chave = models.TextField(verbose_name="Palavras Chave (Separadas por Espaço)")
    
    def __str__(self) -> str:
        return self.nome

class MaterialDeApoio(models.Model):
    class Meta:
        verbose_name_plural = "Materiais de Apoio"
    imagem_material = models.ImageField(upload_to="material_apoio/imgs/%Y/%m", verbose_name="Imagem do Material")
    titulo = models.CharField(max_length=255, verbose_name="Título do Material")
    texto = models.TextField(verbose_name="Texto do Material")
    material = models.FileField(upload_to="material_apoio/pdf/%Y/%m", verbose_name='Material de Apoio')
    categoria = models.CharField(max_length=300, choices=(
        ('Geral', "Geral"),
        ("Especifico", "Especifico")
    ))
    categoria_do_material = models.ForeignKey(to=CategoriaMaterialDeApoio, on_delete=models.PROTECT, verbose_name="Categoria do material",null=True, blank=True)
    palavras_chave_material = models.TextField(verbose_name="Palavras Chave (Separadas por Espaço)")

class Termos(models.Model):
    class Meta:
        verbose_name_plural = "Termos e Condições de uso"
    termo_de_uso = models.TextField(verbose_name="Termo de Uso")
    

    def __str__(self) -> str:
        return "Termo de Uso"

class Video(models.Model):
    class Meta:
        verbose_name_plural = "Videos"
    link = models.CharField(max_length=555, verbose_name="LINK")

class MaterialdeClientes(models.Model):
    class Meta:
        verbose_name_plural = "Materiais dos Clientes"
    usuario = models.CharField(max_length=255, verbose_name="Usuário")
    categoria = models.CharField(max_length=255, verbose_name="Categoria")
    material = models.ImageField(upload_to="material_clientes/%Y/%m", verbose_name='Material do Cliente')
    data_criacao = models.DateField(auto_now_add=False, verbose_name="Data de Criação")