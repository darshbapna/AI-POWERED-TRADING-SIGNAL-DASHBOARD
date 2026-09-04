import React from 'react';
import { Activity, Cpu, RefreshCw, Volume2, VolumeX } from 'lucide-react';

interface HeaderProps {
  wsConnected: boolean;
  soundEnabled: boolean;
  onToggleSound: () => void;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  wsConnected,
  soundEnabled,
  onToggleSound,
  onRefresh,
}) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/90 sticky top-0 z-50 backdrop-blur-md">
      <div className="max-w-[1720px] mx-auto px-4 py-2.5 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-black tracking-wider text-base bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  AURA QUANT
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  v2.0-PRO
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Multi-Asset AI Signal & Sentiment Engine</p>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-2 pl-4 border-l border-slate-800">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-700 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              <span className="text-slate-300 text-[11px]">
                {wsConnected ? 'STREAM ACTIVE' : 'CONNECTING...'}
              </span>
            </div>
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-700 text-xs font-mono">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-300 text-[11px]">GBDT + SHAP + FinBERT</span>
            </div>
          </div>
        </div>

        {/* Action Toggles */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefresh}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Sync Live</span>
          </button>
          <button
            onClick={onToggleSound}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition"
            title="Toggle Sound"
          >
            {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4 text-slate-500" />}
          </button>
        </div>

      </div>
    </header>
  );
};
