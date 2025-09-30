# Calculator Component - Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Install Dependencies
```bash
pip install pytest pytest-cov
```

### Use the Calculator
```python
from src.calculator import Calculator

calc = Calculator()
print(calc.add(10, 5))       # 15
print(calc.subtract(20, 8))  # 12
print(calc.multiply(6, 7))   # 42
print(calc.divide(15, 3))    # 5.0
```

### Run Tests
```bash
pytest tests/test_calculator.py -v
```

### See Examples
```bash
python3 examples/calculator_usage.py
```

## 📚 Common Use Cases

### Financial Calculations (2 decimal places)
```python
calc = Calculator(precision=2)
subtotal = calc.add(29.99, 15.50)
tax = calc.multiply(subtotal, 0.08)
total = calc.add(subtotal, tax)
```

### Scientific Calculations (high precision)
```python
calc = Calculator(precision=15)
pi_approx = calc.divide(22, 7)
```

### Error Handling
```python
from src.calculator import Calculator, DivisionByZeroError

calc = Calculator()
try:
    result = calc.divide(10, 0)
except DivisionByZeroError as e:
    print(f"Error: {e}")
```

### Quick One-Off Calculations
```python
from src.calculator import add, subtract, multiply, divide

total = add(100, 50)        # 150
diff = subtract(100, 50)    # 50
product = multiply(100, 50) # 5000
quotient = divide(100, 50)  # 2.0
```

## 🎯 File Locations

- **Component**: `src/calculator.py`
- **Tests**: `tests/test_calculator.py`
- **Examples**: `examples/calculator_usage.py`
- **Documentation**: `docs/CALCULATOR.md`
- **Summary**: `CALCULATOR_SUMMARY.md`

## ✅ Test Results

- **89 tests** - All passing ✅
- **100% code coverage** ✅
- **0.31s execution time** ⚡

## 📖 Full Documentation

See `docs/CALCULATOR.md` for complete API documentation and advanced usage.

---

**That's it!** You now have a production-ready calculator component. 🎉