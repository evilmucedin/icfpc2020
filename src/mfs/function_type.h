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
  SEND = 15,
  NEGATE = 16,
  S_COMBINATOR = 18,
  C_COMBINATOR = 19,
  B_COMBINATOR = 20,
  K_COMBINATOR = 21,  // Also works as 'True' from boolean operators
  FALSE_SECOND = 22,  // Also works as 'False' from boolean operators
  POWER_OF_TWO = 23,
  I_COMBINATOR = 24,
  CONS = 25,
  CAR = 26,
  END
};
