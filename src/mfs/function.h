#pragma once

#include "expression.h"
#include "function_type.h"

#include <vector>

unsigned ExpectedParameters(FunctionType ftype);

Expression Apply(FunctionType ftype);
Expression Apply(FunctionType ftype, const Expression& e0);
Expression Apply(FunctionType ftype, const Expression& e0,
                 const Expression& e1);
Expression Apply(FunctionType ftype, const Expression& e0, const Expression& e1,
                 const Expression& e2);
Expression Apply(FunctionType ftype, const std::vector<Expression>& v);
