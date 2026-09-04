import React from 'react';
import { Sparkles } from 'lucide-react';
import { ShapDriver } from '../types';

interface ShapExplanationProps {
  drivers: ShapDriver[];
}

export const ShapExplanation: React.FC<ShapExplanationProps> = ({ drivers }) => {
  return (
    <div className="bg-slate-900/75 backdrop-blur-md border border-slate-800 rounded-2xl p-5 flex-1 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-md bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            SHAP Explainability Breakdown
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
          Plain English
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-3">
        TreeExplainer marginal feature contributions driving the AI model log-odds:
      </p>

      <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
        {drivers.map((d, idx) => {
          const isBull = d.direction === 'bullish';
          return (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono font-bold text-slate-300">
                  {d.feature_label}
                </span>
                <span
                  className={`font-mono font-semibold px-2 py-0.5 rounded text-[10px] ${
                    isBull
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  }`}
                >
                  {isBull ? '+' : ''}
                  {d.shap_impact.toFixed(3)} SHAP
                </span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {d.explanation}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
