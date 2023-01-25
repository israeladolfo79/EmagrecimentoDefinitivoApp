from django import forms
from . import models
from django.contrib.auth.models import User

class DadosPessoaisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DadosPessoaisForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['nascimento'].widget = forms.DateInput()
    class Meta:
        model = models.DadosPessoais
        exclude = [
            'assistiu_video',
    ]

class DoencaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DoencaForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Doenca
        exclude = [
            '',
    ]
class MedicamentoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MedicamentoForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Medicamento
        exclude = [
            '',
    ]
class CirurgiaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CirurgiaForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Cirurgia
        exclude = [
            '',
    ]
class ExameSangueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExameSangueForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.ExameSangue
        exclude = [
            '',
    ]
class IntestinoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IntestinoForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Intestino
        exclude = [
            '',
    ]
class MedicamentoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MedicamentoForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Medicamento
        exclude = [
            '',
    ]
class SonoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SonoForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Sono
        exclude = [
            '',
    ]
class AlcoolForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AlcoolForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Alcool
        exclude = [
            '',
    ]
class SuplementoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SuplementoForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Suplemento
        exclude = [
            '',
    ]
class CicloMenstrualForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CicloMenstrualForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.CicloMenstrual
        exclude = [
            '',
    ]
class AntropometricosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AntropometricosForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Antropometricos
        exclude = [
            '',
    ]
class HorariosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HorariosForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['treino'].widget = forms.TimeInput(format="%d%m%Y")
    class Meta:
        model = models.Horarios
        exclude = [
            '',
    ]
        widgets = {
            'treino': forms.TimeField()
        }
class ExerciciosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExerciciosForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
    class Meta:
        model = models.Exercicios
        exclude = [
            '',
    ]