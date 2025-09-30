# Calculator Component

A fully accessible, well-tested React calculator component that supports basic arithmetic operations (addition, subtraction, multiplication, and division).

## Features

- ✅ **Four Basic Operations**: Add, subtract, multiply, and divide
- ✅ **Comprehensive Error Handling**: Graceful handling of division by zero and invalid inputs
- ✅ **Fully Accessible**: WCAG 2.1 compliant with proper ARIA labels and keyboard navigation
- ✅ **Well-Tested**: 100% test coverage with unit and integration tests
- ✅ **TypeScript**: Fully typed for type safety
- ✅ **Clean Architecture**: Separation of concerns with custom hooks and utility functions
- ✅ **Modern UI**: Clean, responsive design with support for high contrast and reduced motion

## Installation

```bash
npm install
```

## Usage

### Basic Usage

```tsx
import { Calculator } from './Calculator';

function App() {
  return (
    <div className="App">
      <Calculator />
    </div>
  );
}
```

### Using the Custom Hook

You can also use the `useCalculator` hook directly in your own components:

```tsx
import { useCalculator } from './useCalculator';

function MyCustomCalculator() {
  const { 
    firstNumber, 
    secondNumber, 
    result, 
    error,
    setFirstNumber,
    setSecondNumber,
    calculate,
    clear
  } = useCalculator();

  return (
    // Your custom UI
  );
}
```

### Using Utility Functions

The utility functions can be used independently:

```tsx
import { add, subtract, multiply, divide, performCalculation } from './calculator.utils';

// Direct operations
const sum = add(5, 3); // 8
const difference = subtract(10, 3); // 7

// With validation
const result = performCalculation('10', '5', 'divide');
if (result.error) {
  console.error(result.error);
} else {
  console.log(result.value); // 2
}
```

## API Reference

### Calculator Component

The main calculator component with a complete UI.

**Props**: None

**Features**:
- Two number inputs
- Four operation radio buttons
- Calculate and Clear buttons
- Error display
- Result display

### useCalculator Hook

Custom hook that manages calculator state and operations.

**Returns**:
```typescript
{
  firstNumber: string;
  secondNumber: string;
  result: number | null;
  error: string | null;
  setFirstNumber: (value: string) => void;
  setSecondNumber: (value: string) => void;
  calculate: (operation: Operation) => void;
  clear: () => void;
}
```

### Utility Functions

#### `performCalculation(a: string, b: string, operation: Operation): CalculationResult`

Performs a calculation with validation and error handling.

**Parameters**:
- `a`: First number as string
- `b`: Second number as string
- `operation`: One of `'add'`, `'subtract'`, `'multiply'`, `'divide'`

**Returns**:
```typescript
{
  value: number;
  error: null;
} | {
  value: null;
  error: string;
}
```

#### Basic Operations

- `add(a: number, b: number): number`
- `subtract(a: number, b: number): number`
- `multiply(a: number, b: number): number`
- `divide(a: number, b: number): number` - Throws error if dividing by zero

#### Validation

- `isValidNumber(value: string): boolean` - Validates if a string can be converted to a valid number

## Error Handling

The calculator handles three types of errors:

1. **Division by Zero**: When attempting to divide by zero
   - Error message: "Cannot divide by zero"

2. **Invalid Number**: When inputs are not valid numbers
   - Error message: "Please enter valid numbers"

3. **Missing Input**: When one or both inputs are empty
   - Error message: "Please enter both numbers"

Errors are displayed with proper ARIA labels and automatically clear when the user starts typing.

## Accessibility Features

- **Keyboard Navigation**: 
  - Press `Enter` to calculate
  - Press `Escape` to clear
  - Tab navigation through all interactive elements

- **Screen Reader Support**:
  - Proper ARIA labels on all inputs and buttons
  - Error messages announced via `role="alert"`
  - Results announced via `role="status"`
  - Invalid inputs marked with `aria-invalid`

- **Visual Accessibility**:
  - High contrast mode support
  - Reduced motion support
  - Focus indicators on all interactive elements
  - Clear error states with visual indicators

## Testing

Run the test suite:

```bash
npm test
```

Run tests with coverage:

```bash
npm test -- --coverage
```

### Test Coverage

The component has comprehensive test coverage including:

- ✅ Component rendering
- ✅ All arithmetic operations (add, subtract, multiply, divide)
- ✅ Error handling (division by zero, invalid inputs, missing inputs)
- ✅ Clear functionality
- ✅ Keyboard interactions
- ✅ Accessibility features
- ✅ Edge cases (large numbers, decimals, floating point precision)
- ✅ Hook functionality
- ✅ Utility functions

## Architecture

The calculator follows clean architecture principles:

```
calculator-component/
├── src/
│   ├── Calculator.tsx          # Main component
│   ├── Calculator.css          # Styles
│   ├── Calculator.types.ts     # TypeScript types
│   ├── useCalculator.ts        # Custom hook
│   ├── calculator.utils.ts     # Utility functions
│   ├── Calculator.test.tsx     # Component tests
│   ├── useCalculator.test.ts   # Hook tests
│   └── calculator.utils.test.ts # Utility tests
├── package.json
├── tsconfig.json
├── jest.config.js
└── README.md
```

### Design Patterns

1. **Separation of Concerns**: 
   - Component handles UI
   - Hook manages state
   - Utils handle business logic

2. **Custom Hooks**: 
   - Encapsulates calculator logic
   - Reusable across components

3. **Type Safety**: 
   - TypeScript for compile-time safety
   - Discriminated unions for result types

4. **Error Handling**: 
   - Explicit error types
   - Graceful error recovery
   - User-friendly error messages

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Write tests for any new features
2. Ensure all tests pass
3. Follow the existing code style
4. Update documentation as needed

## License

MIT

## Authors

Created as a demonstration of best practices for React component development, including proper testing, accessibility, and error handling.