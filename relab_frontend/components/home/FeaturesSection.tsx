// components/home/FeaturesSection.tsx
'use client';

import { Shield, Zap, Sparkles } from 'lucide-react';

export default function FeaturesSection() {
  const features = [
    {
      icon: Shield,
      title: 'Compra Segura',
      description: 'Proteção total em todas as transações',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      icon: Zap,
      title: 'Entrega Rápida',
      description: 'Receba em até 24 horas na sua casa',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Sparkles,
      title: 'Qualidade Premium',
      description: 'Produtos selecionados e verificados',
      gradient: 'from-purple-500 to-pink-500'
    }
  ];

  return (
    <div className="py-20 px-6">
      <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div
              key={index}
              className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:border-white/20 transition-all hover:scale-105"
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}