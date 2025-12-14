function factorial(n) {
  return n < 2 ? 1 : n * factorial(n - 1);
}

console.log("Factorial of 5:", factorial(5));
