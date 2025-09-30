"""
Calculator Component

A simple, well-tested calculator component that performs basic arithmetic operations.
Designed with error handling, type safety, and accessibility in mind.

Author: Auto-generated
Version: 1.0.0
"""

from typing import Union

Number = Union[int, float]


class CalculatorError(Exception):
    """Base exception for calculator-related errors."""
    pass


class DivisionByZeroError(CalculatorError):
    """Raised when attempting to divide by zero."""
    pass


class InvalidInputError(CalculatorError):
    """Raised when invalid input is provided to calculator operations."""
    pass


class Calculator:
    """
    A simple calculator component for basic arithmetic operations.
    
    This calculator supports addition, subtraction, multiplication, and division
    operations on numeric values (int or float). It includes comprehensive error
    handling and input validation.
    
    Features:
        - Type-safe operations with type hints
        - Comprehensive error handling
        - Division by zero protection
        - Input validation
        - Precision handling for floating-point operations
    
    Examples:
        >>> calc = Calculator()
        >>> calc.add(5, 3)
        8
        >>> calc.subtract(10, 4)
        6
        >>> calc.multiply(6, 7)
        42
        >>> calc.divide(15, 3)
        5.0
        >>> calc.divide(10, 0)
        Traceback (most recent call last):
            ...
        DivisionByZeroError: Cannot divide by zero
    """
    
    def __init__(self, precision: int = 10):
        """
        Initialize the Calculator.
        
        Args:
            precision: Number of decimal places to round results to (default: 10)
                      Set to None to disable rounding.
        
        Raises:
            InvalidInputError: If precision is negative.
        """
        if precision is not None and precision < 0:
            raise InvalidInputError("Precision must be a non-negative integer or None")
        self.precision = precision
        self._last_result: Union[Number, None] = None
    
    def _validate_input(self, *args: Number) -> None:
        """
        Validate that all inputs are numeric values.
        
        Args:
            *args: Variable number of values to validate.
        
        Raises:
            InvalidInputError: If any input is not a number (int or float).
        """
        for arg in args:
            if not isinstance(arg, (int, float)):
                raise InvalidInputError(
                    f"Invalid input type: {type(arg).__name__}. "
                    f"Expected int or float."
                )
            if isinstance(arg, bool):  # bool is a subclass of int, exclude it
                raise InvalidInputError(
                    "Invalid input type: bool. Expected int or float."
                )
    
    def _round_result(self, result: Number) -> Number:
        """
        Round the result to the configured precision.
        
        Args:
            result: The numeric result to round.
        
        Returns:
            The rounded result if precision is set, otherwise the original result.
        """
        if self.precision is not None and isinstance(result, float):
            return round(result, self.precision)
        return result
    
    def add(self, a: Number, b: Number) -> Number:
        """
        Add two numbers.
        
        Args:
            a: The first number (addend).
            b: The second number (addend).
        
        Returns:
            The sum of a and b.
        
        Raises:
            InvalidInputError: If either input is not a valid number.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8
            >>> calc.add(2.5, 3.7)
            6.2
            >>> calc.add(-10, 15)
            5
        """
        self._validate_input(a, b)
        result = a + b
        self._last_result = result
        return self._round_result(result)
    
    def subtract(self, a: Number, b: Number) -> Number:
        """
        Subtract the second number from the first.
        
        Args:
            a: The minuend (number to subtract from).
            b: The subtrahend (number to subtract).
        
        Returns:
            The difference (a - b).
        
        Raises:
            InvalidInputError: If either input is not a valid number.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.subtract(10, 4)
            6
            >>> calc.subtract(5.5, 2.3)
            3.2
            >>> calc.subtract(3, 8)
            -5
        """
        self._validate_input(a, b)
        result = a - b
        self._last_result = result
        return self._round_result(result)
    
    def multiply(self, a: Number, b: Number) -> Number:
        """
        Multiply two numbers.
        
        Args:
            a: The first factor (multiplicand).
            b: The second factor (multiplier).
        
        Returns:
            The product of a and b.
        
        Raises:
            InvalidInputError: If either input is not a valid number.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.multiply(6, 7)
            42
            >>> calc.multiply(2.5, 4)
            10.0
            >>> calc.multiply(-3, 5)
            -15
        """
        self._validate_input(a, b)
        result = a * b
        self._last_result = result
        return self._round_result(result)
    
    def divide(self, a: Number, b: Number) -> float:
        """
        Divide the first number by the second.
        
        Args:
            a: The dividend (number to be divided).
            b: The divisor (number to divide by).
        
        Returns:
            The quotient (a / b) as a float.
        
        Raises:
            InvalidInputError: If either input is not a valid number.
            DivisionByZeroError: If attempting to divide by zero.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.divide(15, 3)
            5.0
            >>> calc.divide(7, 2)
            3.5
            >>> calc.divide(10, 0)
            Traceback (most recent call last):
                ...
            DivisionByZeroError: Cannot divide by zero
        """
        self._validate_input(a, b)
        
        if b == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        
        result = a / b
        self._last_result = result
        return self._round_result(result)
    
    def get_last_result(self) -> Union[Number, None]:
        """
        Get the result of the last operation.
        
        Returns:
            The result of the last calculation, or None if no operations performed.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.get_last_result()
            >>> calc.add(5, 3)
            8
            >>> calc.get_last_result()
            8
        """
        return self._last_result
    
    def clear(self) -> None:
        """
        Clear the last result.
        
        Examples:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8
            >>> calc.clear()
            >>> calc.get_last_result()
        """
        self._last_result = None
    
    def __repr__(self) -> str:
        """
        Return a string representation of the Calculator.
        
        Returns:
            A string describing the calculator and its current state.
        """
        return f"Calculator(precision={self.precision}, last_result={self._last_result})"


# Convenience functions for quick calculations without instantiating the class

def add(a: Number, b: Number) -> Number:
    """Convenience function to add two numbers."""
    return Calculator().add(a, b)


def subtract(a: Number, b: Number) -> Number:
    """Convenience function to subtract two numbers."""
    return Calculator().subtract(a, b)


def multiply(a: Number, b: Number) -> Number:
    """Convenience function to multiply two numbers."""
    return Calculator().multiply(a, b)


def divide(a: Number, b: Number) -> float:
    """Convenience function to divide two numbers."""
    return Calculator().divide(a, b)