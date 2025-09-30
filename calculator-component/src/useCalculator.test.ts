import { renderHook, act } from '@testing-library/react';
import { useCalculator } from './useCalculator';

describe('useCalculator', () => {
  describe('Initial State', () => {
    test('initializes with empty values', () => {
      const { result } = renderHook(() => useCalculator());

      expect(result.current.firstNumber).toBe('');
      expect(result.current.secondNumber).toBe('');
      expect(result.current.result).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  describe('setFirstNumber', () => {
    test('updates first number', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('5');
      });

      expect(result.current.firstNumber).toBe('5');
    });

    test('clears error when updating first number', () => {
      const { result } = renderHook(() => useCalculator());

      // Trigger an error
      act(() => {
        result.current.calculate('add');
      });

      expect(result.current.error).not.toBeNull();

      // Update first number
      act(() => {
        result.current.setFirstNumber('5');
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('setSecondNumber', () => {
    test('updates second number', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setSecondNumber('3');
      });

      expect(result.current.secondNumber).toBe('3');
    });

    test('clears error when updating second number', () => {
      const { result } = renderHook(() => useCalculator());

      // Trigger an error
      act(() => {
        result.current.calculate('add');
      });

      expect(result.current.error).not.toBeNull();

      // Update second number
      act(() => {
        result.current.setSecondNumber('3');
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('calculate', () => {
    test('performs addition', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('5');
        result.current.setSecondNumber('3');
        result.current.calculate('add');
      });

      expect(result.current.result).toBe(8);
      expect(result.current.error).toBeNull();
    });

    test('performs subtraction', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('10');
        result.current.setSecondNumber('3');
        result.current.calculate('subtract');
      });

      expect(result.current.result).toBe(7);
      expect(result.current.error).toBeNull();
    });

    test('performs multiplication', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('4');
        result.current.setSecondNumber('5');
        result.current.calculate('multiply');
      });

      expect(result.current.result).toBe(20);
      expect(result.current.error).toBeNull();
    });

    test('performs division', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('20');
        result.current.setSecondNumber('4');
        result.current.calculate('divide');
      });

      expect(result.current.result).toBe(5);
      expect(result.current.error).toBeNull();
    });

    test('sets error for division by zero', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.setFirstNumber('10');
        result.current.setSecondNumber('0');
        result.current.calculate('divide');
      });

      expect(result.current.result).toBeNull();
      expect(result.current.error).toBe('Cannot divide by zero');
    });

    test('sets error for missing inputs', () => {
      const { result } = renderHook(() => useCalculator());

      act(() => {
        result.current.calculate('add');
      });

      expect(result.current.result).toBeNull();
      expect(result.current.error).toBe('Please enter both numbers');
    });
  });

  describe('clear', () => {
    test('clears all state', () => {
      const { result } = renderHook(() => useCalculator());

      // Set some values
      act(() => {
        result.current.setFirstNumber('5');
        result.current.setSecondNumber('3');
        result.current.calculate('add');
      });

      expect(result.current.result).toBe(8);

      // Clear
      act(() => {
        result.current.clear();
      });

      expect(result.current.firstNumber).toBe('');
      expect(result.current.secondNumber).toBe('');
      expect(result.current.result).toBeNull();
      expect(result.current.error).toBeNull();
    });

    test('clears error state', () => {
      const { result } = renderHook(() => useCalculator());

      // Trigger an error
      act(() => {
        result.current.setFirstNumber('10');
        result.current.setSecondNumber('0');
        result.current.calculate('divide');
      });

      expect(result.current.error).not.toBeNull();

      // Clear
      act(() => {
        result.current.clear();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Multiple calculations', () => {
    test('can perform multiple calculations in sequence', () => {
      const { result } = renderHook(() => useCalculator());

      // First calculation
      act(() => {
        result.current.setFirstNumber('5');
        result.current.setSecondNumber('3');
        result.current.calculate('add');
      });

      expect(result.current.result).toBe(8);

      // Second calculation
      act(() => {
        result.current.setFirstNumber('10');
        result.current.setSecondNumber('2');
        result.current.calculate('multiply');
      });

      expect(result.current.result).toBe(20);
    });
  });
});