# pegando uma data passada e subtraindo a data atual para contarr os dias
from datetime import date
from dateutil.relativedelta import relativedelta


def verifica_data(data):
    # verificando se a data já passou
    if data < date.today():
        return 0
    else:
        # pegando a diferença de dias entre a data atual e a data passada
        diferenca = data - date.today()
        return int(diferenca.days)


def validar_cpf(cpf):
    cpf = cpf.replace(".", "").replace("-", "")  # Remove pontos e traços do CPF
    if (
        len(cpf) != 11 or not cpf.isdigit()
    ):  # Verifica se o CPF tem 11 dígitos e se são todos números
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        return False

    # Se chegou até aqui, o CPF é válido
    return True


def calcula_data_expiracao():
    data = date.today() + relativedelta(days=360)
    print(data)
    # retornando data no formato 00/00/0000
    return data.strftime("%d/%m/%Y")
