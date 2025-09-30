import { Operation, CalculationResult, CalculatorError } from './Calculator.types';

/**
 * Validates that a string can be converted to a valid number
 * @param value - The string value to validate
 * @returns true if the value is a valid number
 */
export const isValidNumber = (value: string): boolean => {
  if (value.trim() === '') return false;
  const num = parseFloat(value);
  return !isNaN(num) && isFinite(num);
};

/**
 * Performs addition of two numbers
 * @param a - First number
 * @param b - Second number
 * @returns The sum of a and b
 */
export const add = (a: number, b: number): number => {
  return a + b;
};

/**
 * Performs subtraction of two numbers
 * @param a - First number
 * @param b - Second number
 * @returns The difference of a and b
 */
export const subtract = (a: number, b: number): number => {
  return a - b;
};

/**
 * Performs multiplication of two numbers
 * @param a - First number
 * @param b - Second number
 * @returns The product of a and b
 */
export const multiply = (a: number, b: number): number => {
  return a * b;
};

/**
 * Performs division of two numbers with zero-division check
 * @param a - Dividend
 * @param b - Divisor
 * @returns The quotient of a and b
 * @throws Error if b is zero
 */
export const divide = (a: number, b: number): number => {
  if (b === 0) {
    throw new Error(CalculatorError.DIVISION_BY_ZERO);
  }
  return a / b;
};

/**
 * Performs a calculation based on the operation type
 * @param a - First number
 * @param b - Second number
 * @param operation - The arithmetic operation to perform
 * @returns CalculationResult with either value or error
 */
export const performCalculation = (
  a: string,
  b: string,
  operation: Operation
): CalculationResult => {
  // Validate inputs
  if (!a.trim() || !b.trim()) {
    return {
      value: null,
      error: CalculatorError.MISSING_INPUT,
    };
  }

  if (!isValidNumber(a) || !isValidNumber(b)) {
    return {
      value: null,
      error: CalculatorError.INVALID_NUMBER,
    };
  }

  const numA = parseFloat(a);
  const numB = parseFloat(b);

  try {
    let result: number;

    switch (operation) {
      case 'add':
        result = add(numA, numB);
        break;
      case 'subtract':
        result = subtract(numA, numB);
        break;
      case 'multiply':
        result = multiply(numA, numB);
        break;
      case 'divide':
        result = divide(numA, numB);
        break;
      default:
        return {
          value: null,
          error: 'Invalid operation',
        };
    }

    // Round to avoid floating point precision issues
    const roundedResult = Math.round(result * 1e10) / 1e10;

    return {
      value: roundedResult,
      error: null,
    };
  } catch (error) {
    return {
      value: null,
      error: error instanceof Error ? error.message : 'An unknown error occurred',
    };
  }
};