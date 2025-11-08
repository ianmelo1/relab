# manage.py (já existe, mas vou garantir)
# produtos/management/commands/setup_inicial.py

from django.core.management.base import BaseCommand
from produtos.models import Categoria, Produto


class Command(BaseCommand):
    help = 'Cria dados iniciais para testes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados iniciais...')

        # Criar Categorias
        categorias_data = [
            {'nome': 'Eletrônicos', 'descricao': 'Produtos eletrônicos e tecnologia'},
            {'nome': 'Roupas', 'descricao': 'Vestuário em geral'},
            {'nome': 'Livros', 'descricao': 'Livros e publicações'},
            {'nome': 'Casa e Decoração', 'descricao': 'Itens para casa'},
        ]

        categorias = []
        for cat_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={'descricao': cat_data['descricao']}
            )
            categorias.append(categoria)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Categoria "{categoria.nome}" criada'))

        # Criar Produtos de exemplo
        produtos_data = [
            {
                'nome': 'Notebook Dell Inspiron',
                'descricao': 'Notebook potente para trabalho e estudo',
                'descricao_curta': 'Notebook Dell i5, 8GB RAM',
                'categoria': categorias[0],
                'preco': 3500.00,
                'preco_promocional': 2999.00,
                'estoque': 15,
                'em_destaque': True
            },
            {
                'nome': 'Mouse Logitech MX Master',
                'descricao': 'Mouse ergonômico de alta precisão',
                'descricao_curta': 'Mouse sem fio premium',
                'categoria': categorias[0],
                'preco': 450.00,
                'estoque': 50,
            },
            {
                'nome': 'Camiseta Básica',
                'descricao': 'Camiseta 100% algodão',
                'descricao_curta': 'Camiseta confortável',
                'categoria': categorias[1],
                'preco': 49.90,
                'preco_promocional': 39.90,
                'estoque': 100,
                'em_destaque': True
            },
        ]

        for prod_data in produtos_data:
            produto, created = Produto.objects.get_or_create(
                nome=prod_data['nome'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Produto "{produto.nome}" criado'))

        self.stdout.write(self.style.SUCCESS('\n✅ Setup inicial concluído!'))