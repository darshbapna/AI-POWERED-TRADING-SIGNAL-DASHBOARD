import React from 'react';
import { PredictResponse } from '../types';

interface SignalCardProps {
  prediction: PredictResponse | null;
}

export const SignalCard: React.FC<SignalCardProps> = ({ prediction }) => {
  if (!prediction) {
    return (
      <div className="bg-slate-900/75 backdrop-blur-md border border-slate-800 rounded-2xl p-5 animate-pulse h-64" />
    );
  }

  const isBuy = prediction.signal_code === 'BUY';
  const isSell = prediction.signal_code === 'SELL';

  return (
    <div className="bg-slate-900/75 backdrop-blur-md border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
          <span className="text-xs font-bold font-mono tracking-wider text-slate-400 uppercase">
            AI Forecast Horizon
          </span>
        </div>
        <span className="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-slate-800 text-cyan-400 border border-slate-700">
          5 TRADING DAYS
        </span>
      </div>

      {/* Recommendation Callout */}
      <div className="text-center py-4 bg-slate-950/80 rounded-xl border border-slate-800/90 mb-4">
        <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest block mb-1">
          Directional Signal
        </span>
        <div
          className={`text-3xl font-black tracking-tight uppercase ${
            isBuy ? 'text-emerald-400' : isSell ? 'text-rose-400' : 'text-slate-300'
          }`}
        >
          {prediction.signal}
        </div>
        <span className="text-xs font-mono text-slate-400 mt-1 inline-block">
          {(prediction.confidence * 100).toFixed(1)}% Model Confidence Probability
        </span>
      </div>

      {/* Confidence Bar */}
      <div className="space-y-1.5 mb-4">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-slate-400">Confidence Conviction</span>
          <span
            className={`font-bold ${
              isBuy ? 'text-emerald-400' : isSell ? 'text-rose-400' : 'text-slate-300'
            }`}
          >
            {(prediction.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isBuy
                ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                : isSell
                ? 'bg-gradient-to-r from-rose-500 to-amber-500'
                : 'bg-slate-500'
            }`}
            style={{ width: `${prediction.confidence * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};
