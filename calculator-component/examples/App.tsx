import React from 'react';
import { Calculator } from '../src/Calculator';
import './App.css';

/**
 * Example application demonstrating the Calculator component
 */
function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Calculator Component Demo</h1>
        <p>A fully accessible, well-tested calculator component</p>
      </header>
      
      <main className="app-main">
        <Calculator />
      </main>
      
      <footer className="app-footer">
        <p>
          Features: Error handling, accessibility, keyboard shortcuts (Enter to calculate, Esc to clear)
        </p>
      </footer>
    </div>
  );
}

export default App;