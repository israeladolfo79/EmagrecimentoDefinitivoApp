from rest_framework import serializers
from categorias import models

class DadosPessoaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DadosPessoais
        fields = '__all__'

class DoencasSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Doenca
        fields = '__all__'

class MedicamentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Medicamento
        fields = '__all__'

class CirurgiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cirurgia
        fields = '__all__'

class ExameSangueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExameSangue
        fields = '__all__'

class IntestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Intestino
        fields = '__all__'

class SonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sono
        fields = '__all__'

class AlcoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Alcool
        fields = '__all__'

class SuplementoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Suplemento
        fields = '__all__'

class CiclosMenstruaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CicloMenstrual
        fields = '__all__'

class AntropometricosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Antropometricos
        fields = '__all__'

class HorariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Horarios
        fields = '__all__'

class ExerciciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exercicios
        fields = '__all__'
