#pragma once

#include "expression.h"
#include "function_type.h"

unsigned ExpectedParameters(FunctionType ftype);

Expression Apply(FunctionType ftype);
Expression Apply(FunctionType ftype, Expression& e0);
Expression Apply(FunctionType ftype, Expression& e0, Expression& e1);
Expression Apply(FunctionType ftype, Expression& e0, Expression& e1,
                 Expression& e2);
