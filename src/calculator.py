#!/usr/bin/env python3
"""
Calculator Component

A simple, well-tested calculator component that provides basic arithmetic operations
with proper error handling, type safety, and accessibility features.

This module follows best practices for:
- Component structure
- Error handling
- Type safety
- Documentation
- Accessibility (clear error messages, type hints)
"""

from typing import Union
from decimal import Decimal, InvalidOperation


class CalculatorError(Exception):
    """Base exception class for calculator errors."""
    pass


class DivisionByZeroError(CalculatorError):
    """Exception raised when attempting to divide by zero."""
    pass


class InvalidOperandError(CalculatorError):
    """Exception raised when operands are invalid."""
    pass


class Calculator:
    """
    A simple calculator component for basic arithmetic operations.
    
    This calculator supports addition, subtraction, multiplication, and division
    of two numbers with proper error handling and type safety.
    
    Attributes:
        precision (int): Number of decimal places for results (default: 10)
    
    Example:
        >>> calc = Calculator()
        >>> calc.add(5, 3)
        8.0
        >>> calc.divide(10, 2)
        5.0
        >>> calc.divide(10, 0)
        Traceback (most recent call last):
            ...
        DivisionByZeroError: Cannot divide by zero
    """
    
    def __init__(self, precision: int = 10):
        """
        Initialize the Calculator component.
        
        Args:
            precision (int): Number of decimal places for calculations (default: 10)
        
        Raises:
            ValueError: If precision is negative
        """
        if precision < 0:
            raise ValueError("Precision must be non-negative")
        self.precision = precision
    
    def _validate_operands(self, a: Union[int, float, Decimal], 
                          b: Union[int, float, Decimal]) -> tuple[Decimal, Decimal]:
        """
        Validate and convert operands to Decimal for precise calculations.
        
        Args:
            a: First operand
            b: Second operand
        
        Returns:
            tuple[Decimal, Decimal]: Validated operands as Decimal objects
        
        Raises:
            InvalidOperandError: If operands cannot be converted to numbers
        """
        try:
            # Convert boolean to int first to avoid Decimal conversion issues
            if isinstance(a, bool):
                a = int(a)
            if isinstance(b, bool):
                b = int(b)
            
            decimal_a = Decimal(str(a))
            decimal_b = Decimal(str(b))
            return decimal_a, decimal_b
        except (InvalidOperation, ValueError, TypeError) as e:
            raise InvalidOperandError(
                f"Invalid operands: must be numeric values. Error: {str(e)}"
            )
    
    def _format_result(self, result: Decimal) -> float:
        """
        Format the result to the specified precision.
        
        Args:
            result: The calculation result
        
        Returns:
            float: Formatted result
        """
        try:
            return float(round(result, self.precision))
        except (InvalidOperation, OverflowError):
            # For very large numbers, convert to float directly
            return float(result)
    
    def add(self, a: Union[int, float, Decimal], 
            b: Union[int, float, Decimal]) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            float: Sum of a and b
        
        Raises:
            InvalidOperandError: If operands are invalid
        
        Example:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8.0
            >>> calc.add(2.5, 3.7)
            6.2
        """
        decimal_a, decimal_b = self._validate_operands(a, b)
        result = decimal_a + decimal_b
        return self._format_result(result)
    
    def subtract(self, a: Union[int, float, Decimal], 
                 b: Union[int, float, Decimal]) -> float:
        """
        Subtract two numbers.
        
        Args:
            a: First number (minuend)
            b: Second number (subtrahend)
        
        Returns:
            float: Difference of a and b (a - b)
        
        Raises:
            InvalidOperandError: If operands are invalid
        
        Example:
            >>> calc = Calculator()
            >>> calc.subtract(10, 3)
            7.0
            >>> calc.subtract(5.5, 2.2)
            3.3
        """
        decimal_a, decimal_b = self._validate_operands(a, b)
        result = decimal_a - decimal_b
        return self._format_result(result)
    
    def multiply(self, a: Union[int, float, Decimal], 
                 b: Union[int, float, Decimal]) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            float: Product of a and b
        
        Raises:
            InvalidOperandError: If operands are invalid
        
        Example:
            >>> calc = Calculator()
            >>> calc.multiply(5, 3)
            15.0
            >>> calc.multiply(2.5, 4)
            10.0
        """
        decimal_a, decimal_b = self._validate_operands(a, b)
        result = decimal_a * decimal_b
        return self._format_result(result)
    
    def divide(self, a: Union[int, float, Decimal], 
               b: Union[int, float, Decimal]) -> float:
        """
        Divide two numbers.
        
        Args:
            a: Dividend (number to be divided)
            b: Divisor (number to divide by)
        
        Returns:
            float: Quotient of a divided by b
        
        Raises:
            InvalidOperandError: If operands are invalid
            DivisionByZeroError: If attempting to divide by zero
        
        Example:
            >>> calc = Calculator()
            >>> calc.divide(10, 2)
            5.0
            >>> calc.divide(7, 2)
            3.5
            >>> calc.divide(10, 0)
            Traceback (most recent call last):
                ...
            DivisionByZeroError: Cannot divide by zero
        """
        decimal_a, decimal_b = self._validate_operands(a, b)
        
        if decimal_b == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        
        result = decimal_a / decimal_b
        return self._format_result(result)
    
    def calculate(self, a: Union[int, float, Decimal], 
                  operator: str, 
                  b: Union[int, float, Decimal]) -> float:
        """
        Perform a calculation based on the operator.
        
        Args:
            a: First operand
            operator: Operator symbol ('+', '-', '*', '/')
            b: Second operand
        
        Returns:
            float: Result of the calculation
        
        Raises:
            InvalidOperandError: If operands are invalid
            DivisionByZeroError: If attempting to divide by zero
            ValueError: If operator is not recognized
        
        Example:
            >>> calc = Calculator()
            >>> calc.calculate(5, '+', 3)
            8.0
            >>> calc.calculate(10, '/', 2)
            5.0
        """
        operations = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide
        }
        
        if operator not in operations:
            raise ValueError(
                f"Invalid operator '{operator}'. Must be one of: {', '.join(operations.keys())}"
            )
        
        return operations[operator](a, b)


def create_calculator(precision: int = 10) -> Calculator:
    """
    Factory function to create a Calculator instance.
    
    Args:
        precision (int): Number of decimal places for calculations
    
    Returns:
        Calculator: A new Calculator instance
    
    Example:
        >>> calc = create_calculator()
        >>> calc.add(1, 2)
        3.0
    """
    return Calculator(precision=precision)


# Example usage
if __name__ == "__main__":
    # Demonstrate calculator functionality
    calc = Calculator()
    
    print("Calculator Component Demo")
    print("=" * 50)
    
    # Addition
    result = calc.add(10, 5)
    print(f"10 + 5 = {result}")
    
    # Subtraction
    result = calc.subtract(10, 5)
    print(f"10 - 5 = {result}")
    
    # Multiplication
    result = calc.multiply(10, 5)
    print(f"10 * 5 = {result}")
    
    # Division
    result = calc.divide(10, 5)
    print(f"10 / 5 = {result}")
    
    # Using calculate method
    result = calc.calculate(15, '+', 25)
    print(f"15 + 25 = {result}")
    
    # Error handling example
    print("\nError Handling Demo:")
    try:
        calc.divide(10, 0)
    except DivisionByZeroError as e:
        print(f"✓ Caught division by zero: {e}")
    
    try:
        calc.calculate(10, '%', 5)
    except ValueError as e:
        print(f"✓ Caught invalid operator: {e}")
    
    try:
        calc.add("invalid", 5)
    except InvalidOperandError as e:
        print(f"✓ Caught invalid operand: {e}")