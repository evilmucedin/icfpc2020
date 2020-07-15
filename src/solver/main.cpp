#include "common/numeric/long/multiplication.h"
#include "common/numeric/long/unsigned_io.h"
#include "common/numeric/utils/pow.h"
#include "common/stl/base.h"

using namespace std;

int main() {
  LongUnsigned two(2u);
  cout << PowU(two, 200u) << endl;
  cout << PowU(two, 70u) * PowU(two, 130u) << endl;
  return 0;
}
