import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { SignalCard } from './components/SignalCard';
import { ShapExplanation } from './components/ShapExplanation';
import { AssetSummary, PredictResponse, BacktestResponse, AccuracyResponse } from './types';

export const App: React.FC = () => {
  const [ticker, setTicker] = useState<string>('^NSEI');
  const [assets, setAssets] = useState<AssetSummary[]>([]);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [backtest, setBacktest] = useState<BacktestResponse | null>(null);
  const [accuracy, setAccuracy] = useState<AccuracyResponse | null>(null);
  const [wsConnected, setWsConnected] = useState<boolean>(true);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'backtest' | 'accuracy' | 'portfolio'>('dashboard');

  useEffect(() => {
    fetch('/api/assets')
      .then(res => res.json())
      .then(data => {
        if (data && data.assets) setAssets(data.assets);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!ticker) return;

    fetch(`/api/predict/${encodeURIComponent(ticker)}`)
      .then(res => res.json())
      .then(setPrediction)
      .catch(console.error);

    fetch(`/api/backtest/${encodeURIComponent(ticker)}`)
      .then(res => res.json())
      .then(setBacktest)
      .catch(console.error);

    fetch(`/api/accuracy/${encodeURIComponent(ticker)}`)
      .then(res => res.json())
      .then(setAccuracy)
      .catch(console.error);
  }, [ticker]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      <Header
        wsConnected={wsConnected}
        soundEnabled={soundEnabled}
        onToggleSound={() => setSoundEnabled(!soundEnabled)}
        onRefresh={() => {
          setTicker(t => t);
        }}
      />

      <main className="max-w-[1720px] mx-auto w-full px-4 py-4 flex-1 flex flex-col gap-4">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-2 bg-slate-900/80 p-1 rounded-xl border border-slate-800 w-fit">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'dashboard'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Signal Terminal
          </button>
          <button
            onClick={() => setActiveTab('backtest')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'backtest'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Backtest Suite
          </button>
          <button
            onClick={() => setActiveTab('accuracy')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'accuracy'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Accuracy & T+5 Log
          </button>
        </div>

        {/* Dashboard Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">
          <div className="lg:col-span-8 flex flex-col gap-4">
            <div className="bg-slate-900/75 border border-slate-800 rounded-2xl p-5 h-96 flex items-center justify-center text-slate-500 font-mono text-sm">
              Live Chart & Indicators Active in Standalone SPA
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-4">
            <SignalCard prediction={prediction} />
            {prediction && <ShapExplanation drivers={prediction.shap_drivers} />}
          </div>
        </div>
      </main>
    </div>
  );
};
export default App;
