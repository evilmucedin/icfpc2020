#pragma once

#include "common/linear_algebra/bool/vector.h"

using LEF = la::VectorBool;

LEF LEFEncodeNumber(int64_t value);
int64_t LEFDecodeNumber(const LEF& lef);
