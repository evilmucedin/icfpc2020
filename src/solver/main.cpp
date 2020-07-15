#include "common/numeric/long/multiplication.h"
#include "common/numeric/long/unsigned_io.h"
#include "common/numeric/utils/pow.h"

#include <iostream>

using namespace std;

int main() {
  LongUnsigned two(2u);
  std::cout << PowU(two, 200u) << endl;
  std::cout << PowU(two, 70u) * PowU(two, 130u) << endl;
  return 0;
}
