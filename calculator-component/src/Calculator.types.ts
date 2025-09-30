/**
 * Type definitions for Calculator component
 */

/**
 * Available arithmetic operations
 */
export type Operation = 'add' | 'subtract' | 'multiply' | 'divide';

/**
 * Calculator state interface
 */
export interface CalculatorState {
  firstNumber: string;
  secondNumber: string;
  result: number | null;
  error: string | null;
}

/**
 * Calculator error types
 */
export enum CalculatorError {
  DIVISION_BY_ZERO = 'Cannot divide by zero',
  INVALID_NUMBER = 'Please enter valid numbers',
  MISSING_INPUT = 'Please enter both numbers',
}

/**
 * Calculator operation result
 */
export interface CalculationResult {
  value: number;
  error: null;
} | {
  value: null;
  error: string;
}