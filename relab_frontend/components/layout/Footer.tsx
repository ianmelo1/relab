// components/layout/Footer.tsx
'use client';

import { ShoppingBag, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-950/50 border-t border-white/10 mt-20">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Logo e Descrição */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Relab
              </h3>
            </div>
            <p className="text-gray-400 text-sm">
              Sua loja online de confiança. Produtos de qualidade com os melhores preços.
            </p>
          </div>

          {/* Links Rápidos */}
          <div>
            <h4 className="font-semibold mb-4">Links Rápidos</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><a href="#" className="hover:text-purple-400 transition-colors">Sobre Nós</a></li>
              <li><a href="#produtos" className="hover:text-purple-400 transition-colors">Produtos</a></li>
              <li><a href="#" className="hover:text-purple-400 transition-colors">Promoções</a></li>
              <li><a href="#" className="hover:text-purple-400 transition-colors">Contato</a></li>
            </ul>
          </div>

          {/* Atendimento */}
          <div>
            <h4 className="font-semibold mb-4">Atendimento</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><a href="#" className="hover:text-purple-400 transition-colors">FAQ</a></li>
              <li><a href="#" className="hover:text-purple-400 transition-colors">Política de Troca</a></li>
              <li><a href="#" className="hover:text-purple-400 transition-colors">Rastreamento</a></li>
              <li><a href="#" className="hover:text-purple-400 transition-colors">Termos de Uso</a></li>
            </ul>
          </div>

          {/* Contato */}
          <div>
            <h4 className="font-semibold mb-4">Contato</h4>
            <ul className="space-y-3 text-gray-400 text-sm">
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>contato@relab.com</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>(11) 9999-9999</span>
              </li>
              <li className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span>São Paulo, SP</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/10 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2024 Relab. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  );
}