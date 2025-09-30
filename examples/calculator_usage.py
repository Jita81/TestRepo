"""
Calculator Usage Examples

This file demonstrates how to use the Calculator component in various scenarios.
Run this file to see the calculator in action.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import Calculator, DivisionByZeroError, InvalidInputError


def basic_operations_example():
    """Demonstrate basic arithmetic operations."""
    print("=" * 60)
    print("BASIC OPERATIONS")
    print("=" * 60)
    
    calc = Calculator()
    
    # Addition
    result = calc.add(10, 5)
    print(f"10 + 5 = {result}")
    
    # Subtraction
    result = calc.subtract(20, 8)
    print(f"20 - 8 = {result}")
    
    # Multiplication
    result = calc.multiply(6, 7)
    print(f"6 × 7 = {result}")
    
    # Division
    result = calc.divide(15, 3)
    print(f"15 ÷ 3 = {result}")
    
    print()


def chained_operations_example():
    """Demonstrate chaining operations together."""
    print("=" * 60)
    print("CHAINED OPERATIONS")
    print("=" * 60)
    
    calc = Calculator()
    
    # Calculate: ((100 + 50) * 2 - 75) / 5
    print("Calculating: ((100 + 50) × 2 - 75) ÷ 5")
    
    step1 = calc.add(100, 50)
    print(f"  Step 1: 100 + 50 = {step1}")
    
    step2 = calc.multiply(step1, 2)
    print(f"  Step 2: {step1} × 2 = {step2}")
    
    step3 = calc.subtract(step2, 75)
    print(f"  Step 3: {step2} - 75 = {step3}")
    
    step4 = calc.divide(step3, 5)
    print(f"  Step 4: {step3} ÷ 5 = {step4}")
    
    print(f"\nFinal Result: {step4}")
    print(f"Last Result Stored: {calc.get_last_result()}")
    
    print()


def precision_example():
    """Demonstrate precision handling."""
    print("=" * 60)
    print("PRECISION HANDLING")
    print("=" * 60)
    
    # Default precision (10 decimal places)
    calc_default = Calculator()
    result_default = calc_default.divide(1, 3)
    print(f"Default precision (10): 1 ÷ 3 = {result_default}")
    
    # High precision (15 decimal places)
    calc_high = Calculator(precision=15)
    result_high = calc_high.divide(1, 3)
    print(f"High precision (15):    1 ÷ 3 = {result_high}")
    
    # Low precision (2 decimal places) - useful for currency
    calc_currency = Calculator(precision=2)
    result_currency = calc_currency.divide(10, 3)
    print(f"Currency precision (2):  10 ÷ 3 = ${result_currency}")
    
    # No rounding
    calc_no_round = Calculator(precision=None)
    result_no_round = calc_no_round.divide(1, 3)
    print(f"No rounding:            1 ÷ 3 = {result_no_round}")
    
    print()


def error_handling_example():
    """Demonstrate error handling."""
    print("=" * 60)
    print("ERROR HANDLING")
    print("=" * 60)
    
    calc = Calculator()
    
    # Division by zero
    print("Attempting to divide by zero:")
    try:
        result = calc.divide(10, 0)
    except DivisionByZeroError as e:
        print(f"  ✗ Error caught: {e}")
    
    # Invalid input type
    print("\nAttempting to add a string:")
    try:
        result = calc.add("10", 5)
    except InvalidInputError as e:
        print(f"  ✗ Error caught: {e}")
    
    # Invalid input type (boolean)
    print("\nAttempting to multiply with a boolean:")
    try:
        result = calc.multiply(True, 5)
    except InvalidInputError as e:
        print(f"  ✗ Error caught: {e}")
    
    # Valid operation after errors
    print("\nPerforming valid operation after errors:")
    result = calc.add(10, 5)
    print(f"  ✓ 10 + 5 = {result} (calculator still works!)")
    
    print()


def real_world_example():
    """Demonstrate a real-world calculation scenario."""
    print("=" * 60)
    print("REAL-WORLD SCENARIO: Shopping Cart with Tax")
    print("=" * 60)
    
    # Use 2 decimal precision for currency
    calc = Calculator(precision=2)
    
    # Shopping cart items
    item1_price = 29.99
    item2_price = 15.50
    item3_price = 45.00
    tax_rate = 0.08  # 8% sales tax
    
    print(f"Item 1: ${item1_price}")
    print(f"Item 2: ${item2_price}")
    print(f"Item 3: ${item3_price}")
    
    # Calculate subtotal
    subtotal = calc.add(item1_price, item2_price)
    subtotal = calc.add(subtotal, item3_price)
    print(f"\nSubtotal: ${subtotal}")
    
    # Calculate tax
    tax = calc.multiply(subtotal, tax_rate)
    print(f"Tax (8%): ${tax}")
    
    # Calculate total
    total = calc.add(subtotal, tax)
    print(f"Total: ${total}")
    
    print()


def scientific_calculation_example():
    """Demonstrate scientific calculations."""
    print("=" * 60)
    print("SCIENTIFIC CALCULATIONS")
    print("=" * 60)
    
    calc = Calculator(precision=10)
    
    # Calculate area of a circle: A = πr²
    # Using π ≈ 3.1415926536
    pi = 3.1415926536
    radius = 5
    
    print(f"Calculating area of a circle with radius {radius}")
    print(f"Formula: A = πr²")
    
    radius_squared = calc.multiply(radius, radius)
    print(f"  r² = {radius_squared}")
    
    area = calc.multiply(pi, radius_squared)
    print(f"  A = π × r² = {area}")
    
    print()


def state_management_example():
    """Demonstrate state management features."""
    print("=" * 60)
    print("STATE MANAGEMENT")
    print("=" * 60)
    
    calc = Calculator()
    
    print("Initial state:")
    print(f"  Last result: {calc.get_last_result()}")
    print(f"  Calculator: {calc}")
    
    print("\nPerforming operation: 25 + 75")
    calc.add(25, 75)
    print(f"  Last result: {calc.get_last_result()}")
    print(f"  Calculator: {calc}")
    
    print("\nPerforming operation: 10 × 5")
    calc.multiply(10, 5)
    print(f"  Last result: {calc.get_last_result()}")
    print(f"  Calculator: {calc}")
    
    print("\nClearing calculator state:")
    calc.clear()
    print(f"  Last result: {calc.get_last_result()}")
    print(f"  Calculator: {calc}")
    
    print()


def convenience_functions_example():
    """Demonstrate convenience functions."""
    print("=" * 60)
    print("CONVENIENCE FUNCTIONS")
    print("=" * 60)
    
    # Import convenience functions
    from calculator import add, subtract, multiply, divide
    
    print("Using module-level convenience functions:")
    print(f"  add(10, 5) = {add(10, 5)}")
    print(f"  subtract(20, 8) = {subtract(20, 8)}")
    print(f"  multiply(6, 7) = {multiply(6, 7)}")
    print(f"  divide(15, 3) = {divide(15, 3)}")
    
    print("\nNote: Convenience functions create a new Calculator")
    print("      instance for each operation (no state tracking).")
    
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "CALCULATOR USAGE EXAMPLES" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    basic_operations_example()
    chained_operations_example()
    precision_example()
    error_handling_example()
    real_world_example()
    scientific_calculation_example()
    state_management_example()
    convenience_functions_example()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()