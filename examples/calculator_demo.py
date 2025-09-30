#!/usr/bin/env python3
"""
Calculator Component Demo

This script demonstrates the usage of the Calculator component
with various examples and use cases.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.calculator import (
    Calculator,
    create_calculator,
    DivisionByZeroError,
    InvalidOperandError,
    CalculatorError
)


def demo_basic_operations():
    """Demonstrate basic arithmetic operations."""
    print("\n" + "=" * 60)
    print("BASIC OPERATIONS DEMO")
    print("=" * 60)
    
    calc = Calculator()
    
    # Addition
    result = calc.add(10, 5)
    print(f"Addition:       10 + 5 = {result}")
    
    # Subtraction
    result = calc.subtract(10, 5)
    print(f"Subtraction:    10 - 5 = {result}")
    
    # Multiplication
    result = calc.multiply(10, 5)
    print(f"Multiplication: 10 * 5 = {result}")
    
    # Division
    result = calc.divide(10, 5)
    print(f"Division:       10 / 5 = {result}")


def demo_calculate_method():
    """Demonstrate the generic calculate method."""
    print("\n" + "=" * 60)
    print("CALCULATE METHOD DEMO")
    print("=" * 60)
    
    calc = Calculator()
    
    operations = [
        (15, '+', 25),
        (50, '-', 20),
        (6, '*', 7),
        (100, '/', 4),
    ]
    
    for a, op, b in operations:
        result = calc.calculate(a, op, b)
        print(f"{a} {op} {b} = {result}")


def demo_precision():
    """Demonstrate precision handling."""
    print("\n" + "=" * 60)
    print("PRECISION DEMO")
    print("=" * 60)
    
    # Default precision (10 decimal places)
    calc_default = Calculator()
    result = calc_default.divide(1, 3)
    print(f"Default precision (10): 1 / 3 = {result}")
    
    # Custom precision (2 decimal places)
    calc_2dp = Calculator(precision=2)
    result = calc_2dp.divide(10, 3)
    print(f"2 decimal places:       10 / 3 = {result}")
    
    # High precision (15 decimal places)
    calc_high = Calculator(precision=15)
    result = calc_high.divide(22, 7)
    print(f"15 decimal places:      22 / 7 = {result}")
    
    # Zero precision (integer results)
    calc_int = Calculator(precision=0)
    result = calc_int.divide(10, 3)
    print(f"Zero precision:         10 / 3 = {result}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING DEMO")
    print("=" * 60)
    
    calc = Calculator()
    
    # Division by zero
    print("\n1. Division by Zero:")
    try:
        result = calc.divide(10, 0)
    except DivisionByZeroError as e:
        print(f"   ✓ Caught: {type(e).__name__}: {e}")
    
    # Invalid operands
    print("\n2. Invalid Operands:")
    try:
        result = calc.add("not a number", 5)
    except InvalidOperandError as e:
        print(f"   ✓ Caught: {type(e).__name__}: {e}")
    
    # Invalid operator
    print("\n3. Invalid Operator:")
    try:
        result = calc.calculate(10, '%', 5)
    except ValueError as e:
        print(f"   ✓ Caught: {type(e).__name__}: {e}")
    
    # Catching with base exception
    print("\n4. Using Base Exception (CalculatorError):")
    try:
        result = calc.divide(100, 0)
    except CalculatorError as e:
        print(f"   ✓ Caught with base class: {type(e).__name__}: {e}")


def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO")
    print("=" * 60)
    
    calc = Calculator()
    
    # Working with floats
    print("\n1. Floating Point Numbers:")
    result = calc.add(2.5, 3.7)
    print(f"   2.5 + 3.7 = {result}")
    
    # Working with negative numbers
    print("\n2. Negative Numbers:")
    result = calc.multiply(-5, 4)
    print(f"   -5 * 4 = {result}")
    
    # Working with very small numbers
    print("\n3. Very Small Numbers:")
    result = calc.add(0.0000001, 0.0000002)
    print(f"   0.0000001 + 0.0000002 = {result}")
    
    # Working with very large numbers
    print("\n4. Very Large Numbers:")
    result = calc.multiply(1000000, 2000000)
    print(f"   1,000,000 * 2,000,000 = {result:,.0f}")
    
    # String number conversion
    print("\n5. String Number Conversion:")
    result = calc.add("5.5", "3.2")
    print(f"   \"5.5\" + \"3.2\" = {result}")


def demo_factory_function():
    """Demonstrate the factory function."""
    print("\n" + "=" * 60)
    print("FACTORY FUNCTION DEMO")
    print("=" * 60)
    
    # Create calculator using factory
    calc = create_calculator(precision=3)
    result = calc.divide(22, 7)
    print(f"Calculator created with factory function")
    print(f"22 / 7 with 3 decimal places = {result}")


def demo_financial_calculator():
    """Demonstrate a practical financial calculator use case."""
    print("\n" + "=" * 60)
    print("FINANCIAL CALCULATOR USE CASE")
    print("=" * 60)
    
    # Use 2 decimal places for currency
    calc = Calculator(precision=2)
    
    # Shopping cart calculation
    print("\n📊 Shopping Cart:")
    items = [
        ("Laptop", 999.99, 1),
        ("Mouse", 24.99, 2),
        ("Keyboard", 79.99, 1),
    ]
    
    subtotal = 0
    print(f"{'Item':<15} {'Price':>10} {'Qty':>5} {'Total':>10}")
    print("-" * 45)
    
    for item_name, price, quantity in items:
        item_total = calc.multiply(price, quantity)
        subtotal = calc.add(subtotal, item_total)
        print(f"{item_name:<15} ${price:>9.2f} {quantity:>5} ${item_total:>9.2f}")
    
    print("-" * 45)
    print(f"{'Subtotal:':<15} {' ' * 15} ${subtotal:>9.2f}")
    
    # Calculate tax
    tax_rate = 0.08  # 8% tax
    tax = calc.multiply(subtotal, tax_rate)
    print(f"{'Tax (8%):':<15} {' ' * 15} ${tax:>9.2f}")
    
    # Calculate total
    total = calc.add(subtotal, tax)
    print(f"{'Total:':<15} {' ' * 15} ${total:>9.2f}")
    
    # Calculate discount
    print(f"\n💰 Apply 10% Discount:")
    discount_rate = 0.10
    discount = calc.multiply(total, discount_rate)
    final_total = calc.subtract(total, discount)
    print(f"{'Discount (10%):':<15} {' ' * 15} ${discount:>9.2f}")
    print(f"{'Final Total:':<15} {' ' * 15} ${final_total:>9.2f}")


def demo_scientific_calculator():
    """Demonstrate scientific calculations."""
    print("\n" + "=" * 60)
    print("SCIENTIFIC CALCULATOR USE CASE")
    print("=" * 60)
    
    # Use high precision for scientific calculations
    calc = Calculator(precision=10)
    
    print("\n🔬 Physics Calculations:")
    
    # Calculate velocity (distance / time)
    distance = 100  # meters
    time = 9.58  # seconds
    velocity = calc.divide(distance, time)
    print(f"Velocity = Distance / Time")
    print(f"Velocity = {distance} m / {time} s = {velocity:.2f} m/s")
    
    # Calculate area of a circle (approximation)
    print(f"\n🔵 Circle Area:")
    pi = 3.1415926536
    radius = 5
    radius_squared = calc.multiply(radius, radius)
    area = calc.multiply(pi, radius_squared)
    print(f"Area = π * r²")
    print(f"Area = {pi} * {radius}² = {area:.2f} square units")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CALCULATOR COMPONENT DEMONSTRATION")
    print("=" * 60)
    
    # Run all demos
    demo_basic_operations()
    demo_calculate_method()
    demo_precision()
    demo_error_handling()
    demo_advanced_features()
    demo_factory_function()
    demo_financial_calculator()
    demo_scientific_calculator()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED!")
    print("=" * 60)
    print("\nFor more information, see CALCULATOR_README.md")
    print()


if __name__ == "__main__":
    main()