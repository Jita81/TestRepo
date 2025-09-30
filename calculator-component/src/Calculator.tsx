import React, { useState } from 'react';
import { useCalculator } from './useCalculator';
import { Operation } from './Calculator.types';
import './Calculator.css';

/**
 * Calculator Component
 * 
 * A fully accessible calculator component that supports basic arithmetic operations.
 * Includes comprehensive error handling for division by zero and invalid inputs.
 * 
 * @example
 * ```tsx
 * import { Calculator } from './Calculator';
 * 
 * function App() {
 *   return <Calculator />;
 * }
 * ```
 */
export const Calculator: React.FC = () => {
  const {
    firstNumber,
    secondNumber,
    result,
    error,
    setFirstNumber,
    setSecondNumber,
    calculate,
    clear,
  } = useCalculator();

  const [selectedOperation, setSelectedOperation] = useState<Operation>('add');

  const handleCalculate = () => {
    calculate(selectedOperation);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCalculate();
    } else if (e.key === 'Escape') {
      clear();
    }
  };

  return (
    <div 
      className="calculator"
      role="region"
      aria-label="Calculator"
      onKeyDown={handleKeyPress}
    >
      <h1 className="calculator__title">Simple Calculator</h1>
      
      {/* Input Section */}
      <div className="calculator__inputs">
        <div className="calculator__input-group">
          <label htmlFor="first-number" className="calculator__label">
            First Number
          </label>
          <input
            id="first-number"
            type="number"
            className="calculator__input"
            value={firstNumber}
            onChange={(e) => setFirstNumber(e.target.value)}
            aria-describedby={error ? 'calculator-error' : undefined}
            aria-invalid={!!error}
            placeholder="Enter first number"
          />
        </div>

        <div className="calculator__input-group">
          <label htmlFor="second-number" className="calculator__label">
            Second Number
          </label>
          <input
            id="second-number"
            type="number"
            className="calculator__input"
            value={secondNumber}
            onChange={(e) => setSecondNumber(e.target.value)}
            aria-describedby={error ? 'calculator-error' : undefined}
            aria-invalid={!!error}
            placeholder="Enter second number"
          />
        </div>
      </div>

      {/* Operation Selection */}
      <fieldset className="calculator__operations">
        <legend className="calculator__legend">Select Operation</legend>
        <div className="calculator__operation-buttons">
          <label className="calculator__operation-label">
            <input
              type="radio"
              name="operation"
              value="add"
              checked={selectedOperation === 'add'}
              onChange={(e) => setSelectedOperation(e.target.value as Operation)}
              aria-label="Addition"
            />
            <span className="calculator__operation-text">Add (+)</span>
          </label>

          <label className="calculator__operation-label">
            <input
              type="radio"
              name="operation"
              value="subtract"
              checked={selectedOperation === 'subtract'}
              onChange={(e) => setSelectedOperation(e.target.value as Operation)}
              aria-label="Subtraction"
            />
            <span className="calculator__operation-text">Subtract (−)</span>
          </label>

          <label className="calculator__operation-label">
            <input
              type="radio"
              name="operation"
              value="multiply"
              checked={selectedOperation === 'multiply'}
              onChange={(e) => setSelectedOperation(e.target.value as Operation)}
              aria-label="Multiplication"
            />
            <span className="calculator__operation-text">Multiply (×)</span>
          </label>

          <label className="calculator__operation-label">
            <input
              type="radio"
              name="operation"
              value="divide"
              checked={selectedOperation === 'divide'}
              onChange={(e) => setSelectedOperation(e.target.value as Operation)}
              aria-label="Division"
            />
            <span className="calculator__operation-text">Divide (÷)</span>
          </label>
        </div>
      </fieldset>

      {/* Action Buttons */}
      <div className="calculator__actions">
        <button
          className="calculator__button calculator__button--primary"
          onClick={handleCalculate}
          aria-label="Calculate result"
        >
          Calculate
        </button>
        <button
          className="calculator__button calculator__button--secondary"
          onClick={clear}
          aria-label="Clear calculator"
        >
          Clear
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div
          id="calculator-error"
          className="calculator__error"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}

      {/* Result Display */}
      {result !== null && !error && (
        <div
          className="calculator__result"
          role="status"
          aria-live="polite"
          aria-label="Calculation result"
        >
          <strong>Result:</strong> {result}
        </div>
      )}
    </div>
  );
};

export default Calculator;