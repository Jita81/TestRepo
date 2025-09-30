import { useState, useCallback } from 'react';
import { Operation, CalculatorState } from './Calculator.types';
import { performCalculation } from './calculator.utils';

/**
 * Custom hook for calculator logic
 * 
 * Manages calculator state and operations, providing a clean API
 * for the Calculator component.
 * 
 * @returns Calculator state and methods
 * 
 * @example
 * ```tsx
 * const { 
 *   firstNumber, 
 *   setFirstNumber, 
 *   calculate 
 * } = useCalculator();
 * ```
 */
export const useCalculator = () => {
  const [state, setState] = useState<CalculatorState>({
    firstNumber: '',
    secondNumber: '',
    result: null,
    error: null,
  });

  /**
   * Updates the first number input
   */
  const setFirstNumber = useCallback((value: string) => {
    setState((prev) => ({
      ...prev,
      firstNumber: value,
      error: null, // Clear error when user starts typing
    }));
  }, []);

  /**
   * Updates the second number input
   */
  const setSecondNumber = useCallback((value: string) => {
    setState((prev) => ({
      ...prev,
      secondNumber: value,
      error: null, // Clear error when user starts typing
    }));
  }, []);

  /**
   * Performs the calculation based on the selected operation
   */
  const calculate = useCallback((operation: Operation) => {
    const result = performCalculation(
      state.firstNumber,
      state.secondNumber,
      operation
    );

    setState((prev) => ({
      ...prev,
      result: result.value,
      error: result.error,
    }));
  }, [state.firstNumber, state.secondNumber]);

  /**
   * Clears all calculator state
   */
  const clear = useCallback(() => {
    setState({
      firstNumber: '',
      secondNumber: '',
      result: null,
      error: null,
    });
  }, []);

  return {
    firstNumber: state.firstNumber,
    secondNumber: state.secondNumber,
    result: state.result,
    error: state.error,
    setFirstNumber,
    setSecondNumber,
    calculate,
    clear,
  };
};