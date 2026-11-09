# Erro de regra de negócio com o código HTTP da resposta


class ErroApi(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
