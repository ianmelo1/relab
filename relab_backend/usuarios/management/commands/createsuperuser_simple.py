from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import random

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Cria um superusuário de forma simplificada (apenas email e senha)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email do superusuário')
        parser.add_argument('--password', type=str, help='Senha do superusuário')

    def gerar_cpf_aleatorio(self):
        """Gera um CPF aleatório no formato válido (apenas para testes)"""
        # Gera 9 dígitos aleatórios
        cpf_base = [random.randint(0, 9) for _ in range(9)]

        # Calcula primeiro dígito verificador
        soma = sum((10 - i) * cpf_base[i] for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1
        cpf_base.append(digito1)

        # Calcula segundo dígito verificador
        soma = sum((11 - i) * cpf_base[i] for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2
        cpf_base.append(digito2)

        # Formata no padrão XXX.XXX.XXX-XX
        cpf = ''.join(map(str, cpf_base))
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def gerar_telefone_aleatorio(self):
        """Gera um telefone aleatório no formato válido"""
        ddd = random.randint(11, 99)
        numero = random.randint(90000, 99999)
        final = random.randint(1000, 9999)
        return f"({ddd}) {numero}-{final}"

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')

        # Se não passou por argumento, pede via input
        if not email:
            email = input('Email: ').strip()

        if not password:
            from getpass import getpass
            password = getpass('Senha: ')
            password_confirm = getpass('Confirme a senha: ')

            if password != password_confirm:
                self.stdout.write(self.style.ERROR('❌ As senhas não coincidem!'))
                return

        # Validações básicas
        if not email:
            self.stdout.write(self.style.ERROR('❌ Email é obrigatório!'))
            return

        if len(password) < 8:
            self.stdout.write(self.style.WARNING('⚠️  Aviso: Senha muito curta (mínimo 8 caracteres)'))
            confirma = input('Continuar mesmo assim? [s/N]: ').lower()
            if confirma != 's':
                return

        try:
            # Gera username automático a partir do email
            username = email.split('@')[0]
            base_username = username
            counter = 1

            # Garante que o username seja único
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Gera CPF e telefone únicos aleatórios
            cpf = self.gerar_cpf_aleatorio()
            while Usuario.objects.filter(cpf=cpf).exists():
                cpf = self.gerar_cpf_aleatorio()

            telefone = self.gerar_telefone_aleatorio()

            # Cria o superusuário
            usuario = Usuario.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                cpf=cpf,
                telefone=telefone,
                first_name='Admin',
                last_name='Sistema',
                tipo_usuario='admin'
            )

            self.stdout.write(self.style.SUCCESS(f'✅ Superusuário criado com sucesso!'))
            self.stdout.write(self.style.SUCCESS(f'📧 Email: {email}'))
            self.stdout.write(self.style.SUCCESS(f'👤 Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'📱 CPF: {cpf}'))
            self.stdout.write(self.style.SUCCESS(f'📞 Telefone: {telefone}'))
            self.stdout.write(
                self.style.WARNING(f'⚠️  Dados gerados automaticamente. Atualize no admin se necessário.'))

        except IntegrityError as e:
            if 'email' in str(e).lower():
                self.stdout.write(self.style.ERROR(f'❌ Email "{email}" já existe!'))
            elif 'username' in str(e).lower():
                self.stdout.write(self.style.ERROR(f'❌ Username gerado já existe!'))
            elif 'cpf' in str(e).lower():
                self.stdout.write(self.style.ERROR(f'❌ Erro de CPF duplicado. Tente novamente.'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao criar usuário: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))