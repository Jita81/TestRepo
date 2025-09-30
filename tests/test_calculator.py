"""
Comprehensive test suite for the Calculator component.

This test suite covers:
- Basic arithmetic operations
- Edge cases and boundary conditions
- Error handling and validation
- Type safety
- Precision handling
- State management

Uses pytest for testing framework with fixtures and parametrized tests.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import (
    Calculator,
    CalculatorError,
    DivisionByZeroError,
    InvalidInputError,
    add,
    subtract,
    multiply,
    divide,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def calculator():
    """Provide a fresh Calculator instance for each test."""
    return Calculator()


@pytest.fixture
def calculator_high_precision():
    """Provide a Calculator instance with high precision."""
    return Calculator(precision=15)


@pytest.fixture
def calculator_low_precision():
    """Provide a Calculator instance with low precision (2 decimal places)."""
    return Calculator(precision=2)


@pytest.fixture
def calculator_no_precision():
    """Provide a Calculator instance with no rounding."""
    return Calculator(precision=None)


# ============================================================================
# Test Calculator Initialization
# ============================================================================

class TestCalculatorInitialization:
    """Test calculator initialization and configuration."""
    
    def test_default_initialization(self):
        """Test that calculator initializes with default values."""
        calc = Calculator()
        assert calc.precision == 10
        assert calc.get_last_result() is None
    
    def test_custom_precision(self):
        """Test initialization with custom precision."""
        calc = Calculator(precision=5)
        assert calc.precision == 5
    
    def test_no_precision(self):
        """Test initialization with no precision (None)."""
        calc = Calculator(precision=None)
        assert calc.precision is None
    
    def test_negative_precision_raises_error(self):
        """Test that negative precision raises an error."""
        with pytest.raises(InvalidInputError, match="Precision must be a non-negative integer"):
            Calculator(precision=-1)
    
    def test_calculator_repr(self):
        """Test string representation of calculator."""
        calc = Calculator(precision=5)
        assert "Calculator" in repr(calc)
        assert "precision=5" in repr(calc)


# ============================================================================
# Test Addition
# ============================================================================

class TestAddition:
    """Test addition operation."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 5),
        (0, 0, 0),
        (-5, -3, -8),
        (-10, 15, 5),
        (100, 200, 300),
        (2.5, 3.5, 6.0),
        (1.1, 2.2, 3.3),
        (-7.5, 2.5, -5.0),
    ])
    def test_add_various_numbers(self, calculator, a, b, expected):
        """Test addition with various number combinations."""
        result = calculator.add(a, b)
        assert result == pytest.approx(expected)
    
    def test_add_large_numbers(self, calculator):
        """Test addition with very large numbers."""
        result = calculator.add(10**15, 10**15)
        assert result == 2 * 10**15
    
    def test_add_small_numbers(self, calculator):
        """Test addition with very small numbers."""
        result = calculator.add(0.0001, 0.0002)
        assert result == pytest.approx(0.0003)
    
    def test_add_updates_last_result(self, calculator):
        """Test that addition updates the last result."""
        calculator.add(5, 3)
        assert calculator.get_last_result() == 8
    
    def test_add_invalid_input_string(self, calculator):
        """Test that adding strings raises an error."""
        with pytest.raises(InvalidInputError, match="Invalid input type"):
            calculator.add("5", 3)
    
    def test_add_invalid_input_none(self, calculator):
        """Test that adding None raises an error."""
        with pytest.raises(InvalidInputError):
            calculator.add(None, 5)
    
    def test_add_invalid_input_bool(self, calculator):
        """Test that adding booleans raises an error."""
        with pytest.raises(InvalidInputError, match="Invalid input type: bool"):
            calculator.add(True, 5)


# ============================================================================
# Test Subtraction
# ============================================================================

class TestSubtraction:
    """Test subtraction operation."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (10, 4, 6),
        (5, 5, 0),
        (3, 8, -5),
        (-5, -3, -2),
        (-10, 5, -15),
        (100, 200, -100),
        (5.5, 2.3, 3.2),
        (10.0, 3.5, 6.5),
    ])
    def test_subtract_various_numbers(self, calculator, a, b, expected):
        """Test subtraction with various number combinations."""
        result = calculator.subtract(a, b)
        assert result == pytest.approx(expected)
    
    def test_subtract_large_numbers(self, calculator):
        """Test subtraction with very large numbers."""
        result = calculator.subtract(10**15, 10**14)
        assert result == 9 * 10**14
    
    def test_subtract_updates_last_result(self, calculator):
        """Test that subtraction updates the last result."""
        calculator.subtract(10, 4)
        assert calculator.get_last_result() == 6
    
    def test_subtract_invalid_input(self, calculator):
        """Test that invalid input raises an error."""
        with pytest.raises(InvalidInputError):
            calculator.subtract(10, "4")


# ============================================================================
# Test Multiplication
# ============================================================================

class TestMultiplication:
    """Test multiplication operation."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (6, 7, 42),
        (0, 100, 0),
        (100, 0, 0),
        (-3, 5, -15),
        (-4, -6, 24),
        (2.5, 4, 10.0),
        (1.5, 2.0, 3.0),
        (0.1, 0.2, 0.02),
    ])
    def test_multiply_various_numbers(self, calculator, a, b, expected):
        """Test multiplication with various number combinations."""
        result = calculator.multiply(a, b)
        assert result == pytest.approx(expected)
    
    def test_multiply_large_numbers(self, calculator):
        """Test multiplication with large numbers."""
        result = calculator.multiply(10**8, 10**8)
        assert result == 10**16
    
    def test_multiply_by_zero(self, calculator):
        """Test multiplication by zero."""
        assert calculator.multiply(12345, 0) == 0
        assert calculator.multiply(0, 54321) == 0
    
    def test_multiply_updates_last_result(self, calculator):
        """Test that multiplication updates the last result."""
        calculator.multiply(6, 7)
        assert calculator.get_last_result() == 42
    
    def test_multiply_invalid_input(self, calculator):
        """Test that invalid input raises an error."""
        with pytest.raises(InvalidInputError):
            calculator.multiply(5, [])


# ============================================================================
# Test Division
# ============================================================================

class TestDivision:
    """Test division operation."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (15, 3, 5.0),
        (7, 2, 3.5),
        (10, 5, 2.0),
        (-20, 4, -5.0),
        (-15, -3, 5.0),
        (1, 2, 0.5),
        (1, 3, 0.3333333333),
        (22, 7, 3.1428571429),
    ])
    def test_divide_various_numbers(self, calculator, a, b, expected):
        """Test division with various number combinations."""
        result = calculator.divide(a, b)
        assert result == pytest.approx(expected, rel=1e-9)
    
    def test_divide_by_zero_raises_error(self, calculator):
        """Test that division by zero raises a specific error."""
        with pytest.raises(DivisionByZeroError, match="Cannot divide by zero"):
            calculator.divide(10, 0)
    
    def test_divide_zero_by_number(self, calculator):
        """Test dividing zero by a number."""
        result = calculator.divide(0, 5)
        assert result == 0.0
    
    def test_divide_updates_last_result(self, calculator):
        """Test that division updates the last result."""
        calculator.divide(15, 3)
        assert calculator.get_last_result() == 5.0
    
    def test_divide_invalid_input(self, calculator):
        """Test that invalid input raises an error."""
        with pytest.raises(InvalidInputError):
            calculator.divide(10, "2")
    
    def test_divide_returns_float(self, calculator):
        """Test that division always returns a float."""
        result = calculator.divide(10, 2)
        assert isinstance(result, float)


# ============================================================================
# Test Precision Handling
# ============================================================================

class TestPrecision:
    """Test precision handling in calculations."""
    
    def test_high_precision_division(self, calculator_high_precision):
        """Test division with high precision."""
        result = calculator_high_precision.divide(1, 3)
        # Should have 15 decimal places
        assert result == pytest.approx(0.333333333333333, rel=1e-15)
    
    def test_low_precision_division(self, calculator_low_precision):
        """Test division with low precision (2 decimal places)."""
        result = calculator_low_precision.divide(1, 3)
        assert result == 0.33
    
    def test_no_precision_division(self, calculator_no_precision):
        """Test division with no rounding."""
        result = calculator_no_precision.divide(1, 3)
        # Should be full Python float precision
        assert isinstance(result, float)
        assert len(str(result).split('.')[-1]) > 10
    
    def test_precision_with_addition(self, calculator_low_precision):
        """Test precision with addition of floats."""
        result = calculator_low_precision.add(1.111, 2.222)
        assert result == 3.33
    
    def test_precision_with_multiplication(self, calculator_low_precision):
        """Test precision with multiplication."""
        result = calculator_low_precision.multiply(1.111, 2.222)
        assert result == 2.47


# ============================================================================
# Test State Management
# ============================================================================

class TestStateManagement:
    """Test calculator state management."""
    
    def test_last_result_initially_none(self, calculator):
        """Test that last result is initially None."""
        assert calculator.get_last_result() is None
    
    def test_last_result_updates_with_operations(self, calculator):
        """Test that last result updates with each operation."""
        calculator.add(5, 3)
        assert calculator.get_last_result() == 8
        
        calculator.multiply(4, 2)
        assert calculator.get_last_result() == 8
        
        calculator.divide(10, 2)
        assert calculator.get_last_result() == 5.0
    
    def test_clear_resets_last_result(self, calculator):
        """Test that clear resets the last result."""
        calculator.add(5, 3)
        assert calculator.get_last_result() == 8
        
        calculator.clear()
        assert calculator.get_last_result() is None
    
    def test_operations_after_clear(self, calculator):
        """Test that operations work normally after clear."""
        calculator.add(5, 3)
        calculator.clear()
        calculator.subtract(10, 4)
        assert calculator.get_last_result() == 6


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_calculator_error_hierarchy(self):
        """Test that custom errors inherit from CalculatorError."""
        assert issubclass(DivisionByZeroError, CalculatorError)
        assert issubclass(InvalidInputError, CalculatorError)
    
    def test_invalid_input_error_message(self, calculator):
        """Test that error messages are informative."""
        with pytest.raises(InvalidInputError) as exc_info:
            calculator.add("hello", 5)
        assert "str" in str(exc_info.value)
        assert "Expected int or float" in str(exc_info.value)
    
    def test_division_by_zero_error_message(self, calculator):
        """Test division by zero error message."""
        with pytest.raises(DivisionByZeroError) as exc_info:
            calculator.divide(10, 0)
        assert "Cannot divide by zero" in str(exc_info.value)
    
    @pytest.mark.parametrize("invalid_input", [
        "string",
        [],
        {},
        None,
        True,
        False,
    ])
    def test_various_invalid_inputs(self, calculator, invalid_input):
        """Test that various invalid inputs raise errors."""
        with pytest.raises(InvalidInputError):
            calculator.add(invalid_input, 5)


# ============================================================================
# Test Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_convenience_add(self):
        """Test convenience add function."""
        assert add(5, 3) == 8
    
    def test_convenience_subtract(self):
        """Test convenience subtract function."""
        assert subtract(10, 4) == 6
    
    def test_convenience_multiply(self):
        """Test convenience multiply function."""
        assert multiply(6, 7) == 42
    
    def test_convenience_divide(self):
        """Test convenience divide function."""
        assert divide(15, 3) == 5.0
    
    def test_convenience_divide_by_zero(self):
        """Test convenience divide with zero."""
        with pytest.raises(DivisionByZeroError):
            divide(10, 0)


# ============================================================================
# Test Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic usage scenarios."""
    
    def test_chained_operations(self, calculator):
        """Test multiple operations in sequence."""
        # (5 + 3) = 8
        result1 = calculator.add(5, 3)
        # 8 * 2 = 16
        result2 = calculator.multiply(result1, 2)
        # 16 - 6 = 10
        result3 = calculator.subtract(result2, 6)
        # 10 / 2 = 5.0
        result4 = calculator.divide(result3, 2)
        
        assert result4 == 5.0
        assert calculator.get_last_result() == 5.0
    
    def test_complex_calculation(self, calculator):
        """Test a complex calculation scenario."""
        # Calculate: ((15 + 5) * 2 - 10) / 3
        step1 = calculator.add(15, 5)  # 20
        step2 = calculator.multiply(step1, 2)  # 40
        step3 = calculator.subtract(step2, 10)  # 30
        step4 = calculator.divide(step3, 3)  # 10.0
        
        assert step4 == pytest.approx(10.0)
    
    def test_scientific_calculation(self, calculator):
        """Test calculation with scientific notation."""
        result = calculator.multiply(1.5e10, 2.0e5)
        assert result == pytest.approx(3.0e15)
    
    def test_financial_calculation(self, calculator_low_precision):
        """Test financial calculation with appropriate precision."""
        # Calculate: (100 * 1.05) + 50.75
        interest = calculator_low_precision.multiply(100, 1.05)  # 105.00
        total = calculator_low_precision.add(interest, 50.75)  # 155.75
        
        assert total == 155.75


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_numbers(self, calculator):
        """Test operations with very large numbers."""
        large_num = 10**100
        result = calculator.add(large_num, large_num)
        assert result == 2 * large_num
    
    def test_very_small_numbers(self, calculator):
        """Test operations with very small numbers."""
        small_num = 10**-100
        result = calculator.multiply(small_num, 2)
        assert result == pytest.approx(2 * small_num)
    
    def test_negative_zero(self, calculator):
        """Test handling of negative zero."""
        result = calculator.multiply(-1, 0)
        assert result == 0
    
    def test_infinity_handling(self, calculator):
        """Test that calculator can handle infinity (though may overflow)."""
        # This tests behavior with very large number division
        large = 10**308
        result = calculator.divide(large, 1)
        assert result == pytest.approx(large)
    
    def test_mixed_int_float_operations(self, calculator):
        """Test operations with mixed int and float."""
        result = calculator.add(5, 3.5)
        assert result == 8.5
        assert isinstance(result, float)


# ============================================================================
# Performance Tests (Optional)
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_many_operations(self, calculator):
        """Test that many operations execute quickly."""
        result = 0
        for i in range(1000):
            result = calculator.add(result, 1)
        assert result == 1000
    
    def test_precision_performance(self):
        """Test that different precision settings don't drastically affect performance."""
        calc_high = Calculator(precision=15)
        calc_low = Calculator(precision=2)
        
        # Both should complete quickly
        for _ in range(100):
            calc_high.divide(1, 3)
            calc_low.divide(1, 3)