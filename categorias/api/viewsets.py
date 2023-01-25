from rest_framework import viewsets
from rest_framework.views import APIView
from categorias.api import serializers
from categorias import models
from rest_framework import status
from rest_framework.response import Response
from core.formulas import verifica_plano_alimentar, verifica_usuario

from core.models import Usuario

class BaseViewSet(APIView):
    serializer = ""
    model = ""
    def post(self, request):
        if not Usuario.objects.filter(usuario = request.data['user']).exists():
            return Response(data={'user': "Nome de usuário deve coincidir com usuário existente"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return  Response(data={'created': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request):
        username = request.data['user']
        dias_restantes = verifica_usuario(username)
        if not dias_restantes:
            return Response(data={'user': 'O usuário precisa ter dias restantes para poder acessar esta seção'}, status=status.HTTP_400_BAD_REQUEST)

        print(f'username: {username}')
        usuario_encontrado = self.model.objects.filter(usuario=username).exists()
        print(usuario_encontrado)
        if usuario_encontrado:
            usuario = self.model.objects.get(usuario=username)
            serializer = self.serializer(usuario, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={'user': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)


class UpdataveBaseViewSet(BaseViewSet):
    def patch(self, request):
        if not self.model.objects.filter(user = request.data['user']).exists():
            return Response(data={'user': "Dados com este usuário não foram encontrados"}, status=status.HTTP_400_BAD_REQUEST)
        obj = self.model.objects.get(user=request.data['user'])
        serializer = self.serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return  Response(data={'updated': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DadosPessoaisViewSets(BaseViewSet):
    serializer = serializers.DadosPessoaisSerializer
    model = models.DadosPessoais
            
class DoencasViewSets(UpdataveBaseViewSet):
    serializer = serializers.DoencasSerializer
    model = models.Doenca

class MedicamentosViewSets(UpdataveBaseViewSet):
    serializer = serializers.MedicamentosSerializer
    model = models.Medicamento

class CirurgiaViewSets(UpdataveBaseViewSet):
    serializer = serializers.CirurgiaSerializer
    model = models.Cirurgia

class ExameDeSangueViewSets(UpdataveBaseViewSet):
    serializer = serializers.ExameSangueSerializer
    model = models.ExameSangue

class IntestinoViewSets(UpdataveBaseViewSet):
    serializer = serializers.IntestinoSerializer
    model = models.Intestino

class SonoViewSets(UpdataveBaseViewSet):
    serializer = serializers.SonoSerializer
    model = models.Sono

class AlcoolViewSets(UpdataveBaseViewSet):
    serializer = serializers.AlcoolSerializer
    model = models.Alcool

class SuplementoViewSets(UpdataveBaseViewSet):
    serializer = serializers.SuplementoSerializer
    model = models.Suplemento

class CiclosMenstruaisViewSets(UpdataveBaseViewSet):
    serializer = serializers.CiclosMenstruaisSerializer
    model = models.CicloMenstrual

class AntropometricosViewSets(UpdataveBaseViewSet):
    serializer = serializers.AntropometricosSerializer
    model = models.Antropometricos

class HorariosViewSets(UpdataveBaseViewSet):
    serializer = serializers.HorariosSerializer
    model = models.Horarios

class ExerciciosViewSets(UpdataveBaseViewSet):
    serializer = serializers.ExerciciosSerializer
    model = models.Exercicios