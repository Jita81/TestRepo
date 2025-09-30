import {
  isValidNumber,
  add,
  subtract,
  multiply,
  divide,
  performCalculation,
} from './calculator.utils';
import { CalculatorError } from './Calculator.types';

describe('calculator.utils', () => {
  describe('isValidNumber', () => {
    test('returns true for valid integers', () => {
      expect(isValidNumber('5')).toBe(true);
      expect(isValidNumber('0')).toBe(true);
      expect(isValidNumber('-10')).toBe(true);
    });

    test('returns true for valid decimals', () => {
      expect(isValidNumber('3.14')).toBe(true);
      expect(isValidNumber('-2.5')).toBe(true);
      expect(isValidNumber('0.001')).toBe(true);
    });

    test('returns false for empty strings', () => {
      expect(isValidNumber('')).toBe(false);
      expect(isValidNumber('   ')).toBe(false);
    });

    test('returns false for non-numeric strings', () => {
      expect(isValidNumber('abc')).toBe(false);
      expect(isValidNumber('12abc')).toBe(false);
      expect(isValidNumber('NaN')).toBe(false);
    });

    test('returns false for infinity', () => {
      expect(isValidNumber('Infinity')).toBe(false);
      expect(isValidNumber('-Infinity')).toBe(false);
    });
  });

  describe('add', () => {
    test('adds positive numbers', () => {
      expect(add(5, 3)).toBe(8);
      expect(add(10, 20)).toBe(30);
    });

    test('adds negative numbers', () => {
      expect(add(-5, -3)).toBe(-8);
      expect(add(-10, 5)).toBe(-5);
    });

    test('adds decimals', () => {
      expect(add(2.5, 3.7)).toBe(6.2);
      expect(add(0.1, 0.2)).toBeCloseTo(0.3);
    });

    test('adds zero', () => {
      expect(add(5, 0)).toBe(5);
      expect(add(0, 0)).toBe(0);
    });
  });

  describe('subtract', () => {
    test('subtracts positive numbers', () => {
      expect(subtract(10, 3)).toBe(7);
      expect(subtract(20, 5)).toBe(15);
    });

    test('subtracts negative numbers', () => {
      expect(subtract(-5, -3)).toBe(-2);
      expect(subtract(5, -3)).toBe(8);
    });

    test('subtracts decimals', () => {
      expect(subtract(5.5, 2.3)).toBeCloseTo(3.2);
      expect(subtract(10.1, 0.1)).toBe(10);
    });

    test('handles negative results', () => {
      expect(subtract(5, 10)).toBe(-5);
    });
  });

  describe('multiply', () => {
    test('multiplies positive numbers', () => {
      expect(multiply(5, 3)).toBe(15);
      expect(multiply(10, 10)).toBe(100);
    });

    test('multiplies negative numbers', () => {
      expect(multiply(-5, 3)).toBe(-15);
      expect(multiply(-5, -3)).toBe(15);
    });

    test('multiplies decimals', () => {
      expect(multiply(2.5, 4)).toBe(10);
      expect(multiply(0.5, 0.5)).toBe(0.25);
    });

    test('multiplies by zero', () => {
      expect(multiply(5, 0)).toBe(0);
      expect(multiply(0, 0)).toBe(0);
    });
  });

  describe('divide', () => {
    test('divides positive numbers', () => {
      expect(divide(10, 2)).toBe(5);
      expect(divide(20, 4)).toBe(5);
    });

    test('divides negative numbers', () => {
      expect(divide(-10, 2)).toBe(-5);
      expect(divide(10, -2)).toBe(-5);
      expect(divide(-10, -2)).toBe(5);
    });

    test('divides decimals', () => {
      expect(divide(5.5, 1.1)).toBe(5);
      expect(divide(7.5, 2.5)).toBe(3);
    });

    test('handles decimal results', () => {
      expect(divide(10, 3)).toBeCloseTo(3.333333333);
      expect(divide(1, 3)).toBeCloseTo(0.333333333);
    });

    test('throws error when dividing by zero', () => {
      expect(() => divide(10, 0)).toThrow(CalculatorError.DIVISION_BY_ZERO);
      expect(() => divide(0, 0)).toThrow(CalculatorError.DIVISION_BY_ZERO);
    });
  });

  describe('performCalculation', () => {
    describe('addition', () => {
      test('performs addition correctly', () => {
        const result = performCalculation('5', '3', 'add');
        expect(result.value).toBe(8);
        expect(result.error).toBeNull();
      });
    });

    describe('subtraction', () => {
      test('performs subtraction correctly', () => {
        const result = performCalculation('10', '3', 'subtract');
        expect(result.value).toBe(7);
        expect(result.error).toBeNull();
      });
    });

    describe('multiplication', () => {
      test('performs multiplication correctly', () => {
        const result = performCalculation('4', '5', 'multiply');
        expect(result.value).toBe(20);
        expect(result.error).toBeNull();
      });
    });

    describe('division', () => {
      test('performs division correctly', () => {
        const result = performCalculation('20', '4', 'divide');
        expect(result.value).toBe(5);
        expect(result.error).toBeNull();
      });

      test('returns error for division by zero', () => {
        const result = performCalculation('10', '0', 'divide');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.DIVISION_BY_ZERO);
      });
    });

    describe('input validation', () => {
      test('returns error for empty first number', () => {
        const result = performCalculation('', '5', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.MISSING_INPUT);
      });

      test('returns error for empty second number', () => {
        const result = performCalculation('5', '', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.MISSING_INPUT);
      });

      test('returns error for both empty numbers', () => {
        const result = performCalculation('', '', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.MISSING_INPUT);
      });

      test('returns error for invalid first number', () => {
        const result = performCalculation('abc', '5', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.INVALID_NUMBER);
      });

      test('returns error for invalid second number', () => {
        const result = performCalculation('5', 'xyz', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.INVALID_NUMBER);
      });

      test('returns error for both invalid numbers', () => {
        const result = performCalculation('abc', 'xyz', 'add');
        expect(result.value).toBeNull();
        expect(result.error).toBe(CalculatorError.INVALID_NUMBER);
      });
    });

    describe('floating point precision', () => {
      test('rounds result to avoid precision issues', () => {
        const result = performCalculation('0.1', '0.2', 'add');
        expect(result.value).toBe(0.3);
        expect(result.error).toBeNull();
      });

      test('handles very small numbers', () => {
        const result = performCalculation('0.0000000001', '0.0000000002', 'add');
        expect(result.value).toBeCloseTo(0.0000000003, 10);
        expect(result.error).toBeNull();
      });
    });
  });\n});