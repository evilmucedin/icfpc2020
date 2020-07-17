#pragma once

enum class FunctionType {
  NONE,
  SUCCESSOR = 5,
  PREDECESSOR = 6,
  SUM = 7,
  PRODUCT = 9,
  DIVISION = 10,
  EQUALITY = 11,
  STRICT_LESS = 12,
  MODULATE = 13,
  DEMODULATE = 14,
  F15 = 15,  // SEND
  NEGATE = 16,
  S_COMBINATOR = 18,
  F19 = 19,
  B_COMBINATOR = 20,
  K_COMBINATOR = 21,  // Also works as 'True' from boolean operators
  FALSE_SECOND = 22,
  END
};
