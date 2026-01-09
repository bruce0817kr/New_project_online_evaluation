import React from 'react';
import SplitViewEvaluator from '../components/evaluator/SplitViewEvaluator';

function EvaluatorPage() {
  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white shadow-sm px-6 py-4">
        <h1 className="text-2xl font-bold">평가 심사</h1>
      </header>

      <main className="flex-1 overflow-hidden">
        <SplitViewEvaluator />
      </main>
    </div>
  );
}

export default EvaluatorPage;
