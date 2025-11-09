# produtos/management/commands/setup_inicial.py

from django.core.management.base import BaseCommand
from produtos.models import Categoria, Produto
from decimal import Decimal


class Command(BaseCommand):
    help = 'Cria dados iniciais para testes (categorias e produtos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Apaga todos os produtos e categorias antes de criar novos',
        )

    def handle(self, *args, **kwargs):
        reset = kwargs.get('reset', False)

        if reset:
            self.stdout.write(self.style.WARNING('🗑️  Apagando dados existentes...'))
            Produto.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Dados apagados'))

        self.stdout.write(self.style.HTTP_INFO('📦 Criando dados iniciais...'))

        # Criar Categorias (slug será gerado automaticamente pelo model)
        categorias_data = [
            {
                'nome': 'Eletrônicos',
                'descricao': 'Produtos eletrônicos e tecnologia de ponta',
                'ativo': True
            },
            {
                'nome': 'Roupas',
                'descricao': 'Vestuário e moda para todas as ocasiões',
                'ativo': True
            },
            {
                'nome': 'Livros',
                'descricao': 'Livros, publicações e materiais educativos',
                'ativo': True
            },
            {
                'nome': 'Casa e Decoração',
                'descricao': 'Itens para tornar sua casa mais bonita e funcional',
                'ativo': True
            },
            {
                'nome': 'Esportes',
                'descricao': 'Equipamentos e acessórios esportivos',
                'ativo': True
            },
        ]

        categorias = {}
        for cat_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            categorias[cat_data['nome']] = categoria
            status = '✨ criada' if created else '✓ já existe'
            self.stdout.write(self.style.SUCCESS(f'{status}: Categoria "{categoria.nome}"'))

        # Criar Produtos de exemplo
        produtos_data = [
            # Eletrônicos
            {
                'nome': 'Notebook Dell Inspiron 15',
                'descricao': 'Notebook potente para trabalho e estudo. Processador Intel Core i5 11ª geração, 8GB RAM DDR4, SSD 256GB, Tela 15.6" Full HD, Windows 11',
                'descricao_curta': 'Notebook Dell i5, 8GB RAM, SSD 256GB',
                'categoria': categorias['Eletrônicos'],
                'preco': Decimal('3500.00'),
                'preco_promocional': Decimal('2999.00'),
                'estoque': 15,
                'em_destaque': True,
                'ativo': True
            },
            {
                'nome': 'Mouse Logitech MX Master 3',
                'descricao': 'Mouse ergonômico de alta precisão com tecnologia MagSpeed e conexão bluetooth. Perfeito para profissionais.',
                'descricao_curta': 'Mouse sem fio premium ergonômico',
                'categoria': categorias['Eletrônicos'],
                'preco': Decimal('450.00'),
                'estoque': 50,
                'ativo': True
            },
            {
                'nome': 'Teclado Mecânico Keychron K2',
                'descricao': 'Teclado mecânico compacto com switches Gateron, RGB, conexão wireless e com fio. Layout 75%.',
                'descricao_curta': 'Teclado mecânico wireless RGB',
                'categoria': categorias['Eletrônicos'],
                'preco': Decimal('680.00'),
                'preco_promocional': Decimal('599.00'),
                'estoque': 30,
                'em_destaque': True,
                'ativo': True
            },
            {
                'nome': 'Fone de Ouvido Sony WH-1000XM5',
                'descricao': 'Fone com cancelamento de ruído líder de mercado, som Hi-Res, 30h de bateria.',
                'descricao_curta': 'Fone premium com cancelamento de ruído',
                'categoria': categorias['Eletrônicos'],
                'preco': Decimal('1899.00'),
                'estoque': 20,
                'ativo': True
            },
            {
                'nome': 'Monitor LG UltraWide 29"',
                'descricao': 'Monitor ultrawide 29" Full HD, IPS, 75Hz, FreeSync, ideal para produtividade.',
                'descricao_curta': 'Monitor ultrawide 29" IPS',
                'categoria': categorias['Eletrônicos'],
                'preco': Decimal('1299.00'),
                'preco_promocional': Decimal('1099.00'),
                'estoque': 12,
                'ativo': True
            },

            # Roupas
            {
                'nome': 'Camiseta Básica Premium',
                'descricao': 'Camiseta 100% algodão egípcio, corte regular, disponível em várias cores. Qualidade superior.',
                'descricao_curta': 'Camiseta 100% algodão premium',
                'categoria': categorias['Roupas'],
                'preco': Decimal('49.90'),
                'preco_promocional': Decimal('39.90'),
                'estoque': 100,
                'em_destaque': True,
                'ativo': True
            },
            {
                'nome': 'Calça Jeans Slim Fit',
                'descricao': 'Calça jeans de alta qualidade, corte slim, 98% algodão e 2% elastano para mais conforto.',
                'descricao_curta': 'Calça jeans slim confortável',
                'categoria': categorias['Roupas'],
                'preco': Decimal('189.90'),
                'estoque': 60,
                'ativo': True
            },
            {
                'nome': 'Jaqueta de Couro Sintético',
                'descricao': 'Jaqueta estilosa em couro sintético, forrada, com zíperes e bolsos funcionais.',
                'descricao_curta': 'Jaqueta de couro estilosa',
                'categoria': categorias['Roupas'],
                'preco': Decimal('299.00'),
                'preco_promocional': Decimal('249.00'),
                'estoque': 25,
                'ativo': True
            },

            # Livros
            {
                'nome': 'Clean Code - Robert Martin',
                'descricao': 'Livro essencial sobre boas práticas de programação e código limpo.',
                'descricao_curta': 'Guia de código limpo',
                'categoria': categorias['Livros'],
                'preco': Decimal('79.90'),
                'estoque': 45,
                'em_destaque': True,
                'ativo': True
            },
            {
                'nome': 'O Poder do Hábito',
                'descricao': 'Bestseller sobre como os hábitos funcionam e como transformá-los.',
                'descricao_curta': 'Livro sobre transformação de hábitos',
                'categoria': categorias['Livros'],
                'preco': Decimal('45.90'),
                'estoque': 80,
                'ativo': True
            },

            # Casa e Decoração
            {
                'nome': 'Luminária de Mesa LED',
                'descricao': 'Luminária moderna com LED ajustável, 3 níveis de brilho, design minimalista.',
                'descricao_curta': 'Luminária LED ajustável',
                'categoria': categorias['Casa e Decoração'],
                'preco': Decimal('129.90'),
                'estoque': 40,
                'ativo': True
            },
            {
                'nome': 'Kit 4 Quadros Decorativos',
                'descricao': 'Conjunto de 4 quadros com moldura em MDF, tema natureza, 30x40cm cada.',
                'descricao_curta': 'Kit quadros decorativos natureza',
                'categoria': categorias['Casa e Decoração'],
                'preco': Decimal('199.00'),
                'preco_promocional': Decimal('159.00'),
                'estoque': 35,
                'ativo': True
            },

            # Esportes
            {
                'nome': 'Tênis Nike Air Zoom Pegasus',
                'descricao': 'Tênis de corrida com tecnologia Air Zoom, amortecimento responsivo, indicado para treinos.',
                'descricao_curta': 'Tênis de corrida Nike',
                'categoria': categorias['Esportes'],
                'preco': Decimal('599.00'),
                'preco_promocional': Decimal('499.00'),
                'estoque': 50,
                'em_destaque': True,
                'ativo': True
            },
            {
                'nome': 'Garrafa Térmica Stanley 1L',
                'descricao': 'Garrafa térmica mantém temperatura por 24h, ideal para atividades ao ar livre.',
                'descricao_curta': 'Garrafa térmica 1 litro',
                'categoria': categorias['Esportes'],
                'preco': Decimal('189.90'),
                'estoque': 70,
                'ativo': True
            },
        ]

        produtos_criados = 0
        produtos_existentes = 0

        for prod_data in produtos_data:
            produto, created = Produto.objects.get_or_create(
                nome=prod_data['nome'],
                defaults=prod_data
            )

            if created:
                produtos_criados += 1
                preco_info = f"R$ {produto.preco}"
                if produto.preco_promocional:
                    preco_info += f" → R$ {produto.preco_promocional} 🔥"

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✨ Produto criado: "{produto.nome}" ({preco_info})'
                    )
                )
            else:
                produtos_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Já existe: "{produto.nome}"')
                )

        # Resumo final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ Setup inicial concluído!'))
        self.stdout.write(self.style.SUCCESS(f'📂 Categorias: {len(categorias)} criadas/verificadas'))
        self.stdout.write(self.style.SUCCESS(f'✨ Produtos novos: {produtos_criados}'))
        if produtos_existentes > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Produtos já existentes: {produtos_existentes}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('💡 Dica: Use --reset para apagar e recriar todos os dados')