#!/usr/bin/env python3
"""
Comprehensive test suite for the Calculator component.

This test suite follows best practices for testing:
- Comprehensive coverage of all functionality
- Edge case testing
- Error condition testing
- Clear test naming and documentation
- Isolated, independent tests
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.calculator import (
    Calculator,
    CalculatorError,
    DivisionByZeroError,
    InvalidOperandError,
    create_calculator
)


class TestCalculatorInitialization:
    """Test calculator initialization and configuration."""
    
    def test_default_initialization(self):
        """Test calculator initializes with default precision."""
        calc = Calculator()
        assert calc.precision == 10
    
    def test_custom_precision(self):
        """Test calculator initializes with custom precision."""
        calc = Calculator(precision=5)
        assert calc.precision == 5
    
    def test_zero_precision(self):
        """Test calculator accepts zero precision."""
        calc = Calculator(precision=0)
        assert calc.precision == 0
    
    def test_negative_precision_raises_error(self):
        """Test calculator rejects negative precision."""
        with pytest.raises(ValueError, match="Precision must be non-negative"):
            Calculator(precision=-1)


class TestCalculatorAddition:
    """Test addition functionality."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_add_positive_integers(self, calc):
        """Test adding two positive integers."""
        result = calc.add(5, 3)
        assert result == 8.0
    
    def test_add_negative_integers(self, calc):
        """Test adding two negative integers."""
        result = calc.add(-5, -3)
        assert result == -8.0
    
    def test_add_positive_and_negative(self, calc):
        """Test adding positive and negative integers."""
        result = calc.add(10, -3)
        assert result == 7.0
    
    def test_add_floats(self, calc):
        """Test adding floating point numbers."""
        result = calc.add(2.5, 3.7)
        assert result == pytest.approx(6.2)
    
    def test_add_zero(self, calc):
        """Test adding zero."""
        result = calc.add(5, 0)
        assert result == 5.0
    
    def test_add_large_numbers(self, calc):
        """Test adding large numbers."""
        result = calc.add(1000000, 2000000)
        assert result == 3000000.0
    
    def test_add_decimals(self, calc):
        """Test adding Decimal objects."""
        result = calc.add(Decimal('1.1'), Decimal('2.2'))
        assert result == pytest.approx(3.3)
    
    def test_add_with_precision(self):
        """Test addition respects precision setting."""
        calc = Calculator(precision=2)
        result = calc.add(1.111, 2.222)
        assert result == 3.33
    
    def test_add_invalid_first_operand(self, calc):
        """Test adding with invalid first operand."""
        with pytest.raises(InvalidOperandError, match="Invalid operands"):
            calc.add("invalid", 5)
    
    def test_add_invalid_second_operand(self, calc):
        """Test adding with invalid second operand."""
        with pytest.raises(InvalidOperandError, match="Invalid operands"):
            calc.add(5, "invalid")
    
    def test_add_none_operands(self, calc):
        """Test adding with None operands."""
        with pytest.raises(InvalidOperandError):
            calc.add(None, 5)


class TestCalculatorSubtraction:
    """Test subtraction functionality."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_subtract_positive_integers(self, calc):
        """Test subtracting two positive integers."""
        result = calc.subtract(10, 3)
        assert result == 7.0
    
    def test_subtract_negative_integers(self, calc):
        """Test subtracting two negative integers."""
        result = calc.subtract(-10, -3)
        assert result == -7.0
    
    def test_subtract_resulting_in_negative(self, calc):
        """Test subtraction resulting in negative number."""
        result = calc.subtract(3, 10)
        assert result == -7.0
    
    def test_subtract_floats(self, calc):
        """Test subtracting floating point numbers."""
        result = calc.subtract(5.5, 2.2)
        assert result == pytest.approx(3.3)
    
    def test_subtract_zero(self, calc):
        """Test subtracting zero."""
        result = calc.subtract(5, 0)
        assert result == 5.0
    
    def test_subtract_from_zero(self, calc):
        """Test subtracting from zero."""
        result = calc.subtract(0, 5)
        assert result == -5.0
    
    def test_subtract_same_numbers(self, calc):
        """Test subtracting same numbers results in zero."""
        result = calc.subtract(5, 5)
        assert result == 0.0
    
    def test_subtract_decimals(self, calc):
        """Test subtracting Decimal objects."""
        result = calc.subtract(Decimal('5.5'), Decimal('2.2'))
        assert result == pytest.approx(3.3)
    
    def test_subtract_with_precision(self):
        """Test subtraction respects precision setting."""
        calc = Calculator(precision=2)
        result = calc.subtract(5.555, 2.222)
        assert result == 3.33


class TestCalculatorMultiplication:
    """Test multiplication functionality."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_multiply_positive_integers(self, calc):
        """Test multiplying two positive integers."""
        result = calc.multiply(5, 3)
        assert result == 15.0
    
    def test_multiply_negative_integers(self, calc):
        """Test multiplying two negative integers."""
        result = calc.multiply(-5, -3)
        assert result == 15.0
    
    def test_multiply_positive_and_negative(self, calc):
        """Test multiplying positive and negative integers."""
        result = calc.multiply(5, -3)
        assert result == -15.0
    
    def test_multiply_floats(self, calc):
        """Test multiplying floating point numbers."""
        result = calc.multiply(2.5, 4.0)
        assert result == pytest.approx(10.0)
    
    def test_multiply_by_zero(self, calc):
        """Test multiplying by zero."""
        result = calc.multiply(5, 0)
        assert result == 0.0
    
    def test_multiply_by_one(self, calc):
        """Test multiplying by one."""
        result = calc.multiply(5, 1)
        assert result == 5.0
    
    def test_multiply_large_numbers(self, calc):
        """Test multiplying large numbers."""
        result = calc.multiply(1000, 2000)
        assert result == 2000000.0
    
    def test_multiply_decimals(self, calc):
        """Test multiplying Decimal objects."""
        result = calc.multiply(Decimal('2.5'), Decimal('4.0'))
        assert result == pytest.approx(10.0)
    
    def test_multiply_with_precision(self):
        """Test multiplication respects precision setting."""
        calc = Calculator(precision=2)
        result = calc.multiply(3.333, 3.0)
        assert result == 10.0  # 9.999 rounded to 2 places = 10.0


class TestCalculatorDivision:
    """Test division functionality."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_divide_positive_integers(self, calc):
        """Test dividing two positive integers."""
        result = calc.divide(10, 2)
        assert result == 5.0
    
    def test_divide_negative_integers(self, calc):
        """Test dividing two negative integers."""
        result = calc.divide(-10, -2)
        assert result == 5.0
    
    def test_divide_positive_by_negative(self, calc):
        """Test dividing positive by negative integer."""
        result = calc.divide(10, -2)
        assert result == -5.0
    
    def test_divide_resulting_in_float(self, calc):
        """Test division resulting in floating point."""
        result = calc.divide(7, 2)
        assert result == 3.5
    
    def test_divide_floats(self, calc):
        """Test dividing floating point numbers."""
        result = calc.divide(10.0, 4.0)
        assert result == 2.5
    
    def test_divide_by_one(self, calc):
        """Test dividing by one."""
        result = calc.divide(5, 1)
        assert result == 5.0
    
    def test_divide_zero_by_number(self, calc):
        """Test dividing zero by a number."""
        result = calc.divide(0, 5)
        assert result == 0.0
    
    def test_divide_by_zero_raises_error(self, calc):
        """Test dividing by zero raises appropriate error."""
        with pytest.raises(DivisionByZeroError, match="Cannot divide by zero"):
            calc.divide(10, 0)
    
    def test_divide_by_zero_float_raises_error(self, calc):
        """Test dividing by zero (float) raises appropriate error."""
        with pytest.raises(DivisionByZeroError):
            calc.divide(10, 0.0)
    
    def test_divide_decimals(self, calc):
        """Test dividing Decimal objects."""
        result = calc.divide(Decimal('10'), Decimal('2'))
        assert result == 5.0
    
    def test_divide_with_precision(self):
        """Test division respects precision setting."""
        calc = Calculator(precision=2)
        result = calc.divide(10, 3)
        assert result == 3.33
    
    def test_divide_with_high_precision(self):
        """Test division with high precision."""
        calc = Calculator(precision=10)
        result = calc.divide(1, 3)
        assert abs(result - 0.3333333333) < 1e-10


class TestCalculatorCalculateMethod:
    """Test the generic calculate method."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_calculate_addition(self, calc):
        """Test calculate method with addition operator."""
        result = calc.calculate(5, '+', 3)
        assert result == 8.0
    
    def test_calculate_subtraction(self, calc):
        """Test calculate method with subtraction operator."""
        result = calc.calculate(10, '-', 3)
        assert result == 7.0
    
    def test_calculate_multiplication(self, calc):
        """Test calculate method with multiplication operator."""
        result = calc.calculate(5, '*', 3)
        assert result == 15.0
    
    def test_calculate_division(self, calc):
        """Test calculate method with division operator."""
        result = calc.calculate(10, '/', 2)
        assert result == 5.0
    
    def test_calculate_invalid_operator(self, calc):
        """Test calculate method with invalid operator."""
        with pytest.raises(ValueError, match="Invalid operator"):
            calc.calculate(5, '%', 3)
    
    def test_calculate_empty_operator(self, calc):
        """Test calculate method with empty operator."""
        with pytest.raises(ValueError, match="Invalid operator"):
            calc.calculate(5, '', 3)
    
    def test_calculate_division_by_zero(self, calc):
        """Test calculate method handles division by zero."""
        with pytest.raises(DivisionByZeroError):
            calc.calculate(10, '/', 0)


class TestCalculatorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def calc(self):
        """Provide a calculator instance for tests."""
        return Calculator()
    
    def test_very_small_numbers(self, calc):
        """Test operations with very small numbers."""
        result = calc.add(0.0000001, 0.0000002)
        assert result == pytest.approx(0.0000003)
    
    def test_very_large_numbers(self, calc):
        """Test operations with very large numbers."""
        result = calc.multiply(1e10, 1e10)
        assert result == pytest.approx(1e20)
    
    def test_mixed_types(self, calc):
        """Test operations with mixed numeric types."""
        result = calc.add(5, 3.5)
        assert result == 8.5
        
        result = calc.multiply(Decimal('2.5'), 4)
        assert result == pytest.approx(10.0)
    
    def test_string_numbers_accepted(self, calc):
        """Test that string numbers are accepted and converted."""
        # String representations of numbers should be accepted
        result = calc.add("5", "3")
        assert result == 8.0
    
    def test_boolean_values_as_numbers(self, calc):
        """Test boolean values are handled (True=1, False=0)."""
        # Booleans are converted to integers (True=1, False=0)
        result = calc.add(True, False)
        assert result == 1.0
        
        result = calc.multiply(True, True)
        assert result == 1.0
        
        result = calc.add(False, False)
        assert result == 0.0
    
    def test_list_operands_rejected(self, calc):
        """Test that list operands are rejected."""
        with pytest.raises(InvalidOperandError):
            calc.add([1, 2], 3)


class TestCalculatorFactoryFunction:
    """Test the factory function for creating calculators."""
    
    def test_create_calculator_default(self):
        """Test factory function creates calculator with default precision."""
        calc = create_calculator()
        assert isinstance(calc, Calculator)
        assert calc.precision == 10
    
    def test_create_calculator_custom_precision(self):
        """Test factory function creates calculator with custom precision."""
        calc = create_calculator(precision=5)
        assert isinstance(calc, Calculator)
        assert calc.precision == 5
    
    def test_factory_calculator_works(self):
        """Test calculator created by factory works correctly."""
        calc = create_calculator()
        result = calc.add(5, 3)
        assert result == 8.0


class TestCalculatorExceptions:
    """Test custom exception hierarchy."""
    
    def test_division_by_zero_is_calculator_error(self):
        """Test DivisionByZeroError is a CalculatorError."""
        assert issubclass(DivisionByZeroError, CalculatorError)
    
    def test_invalid_operand_is_calculator_error(self):
        """Test InvalidOperandError is a CalculatorError."""
        assert issubclass(InvalidOperandError, CalculatorError)
    
    def test_calculator_error_is_exception(self):
        """Test CalculatorError is an Exception."""
        assert issubclass(CalculatorError, Exception)
    
    def test_can_catch_with_base_exception(self):
        """Test errors can be caught using base CalculatorError."""
        calc = Calculator()
        
        with pytest.raises(CalculatorError):
            calc.divide(10, 0)
        
        with pytest.raises(CalculatorError):
            calc.add("invalid", 5)


class TestCalculatorPrecision:
    """Test precision handling across all operations."""
    
    def test_addition_precision_2(self):
        """Test addition with 2 decimal places precision."""
        calc = Calculator(precision=2)
        result = calc.add(1.111, 2.222)
        assert result == 3.33
    
    def test_subtraction_precision_2(self):
        """Test subtraction with 2 decimal places precision."""
        calc = Calculator(precision=2)
        result = calc.subtract(5.555, 2.222)
        assert result == 3.33
    
    def test_multiplication_precision_2(self):
        """Test multiplication with 2 decimal places precision."""
        calc = Calculator(precision=2)
        result = calc.multiply(3.333, 3.0)
        assert result == 10.0
    
    def test_division_precision_2(self):
        """Test division with 2 decimal places precision."""
        calc = Calculator(precision=2)
        result = calc.divide(10, 3)
        assert result == 3.33
    
    def test_zero_precision(self):
        """Test operations with zero precision (integer results)."""
        calc = Calculator(precision=0)
        result = calc.divide(10, 3)
        assert result == 3.0


# Run tests with coverage if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])