#pragma once

#include "expression.h"
#include "function_type.h"

#include <vector>

unsigned ExpectedParameters(FunctionType ftype);

Expression Evaluate(FunctionType ftype);
Expression Evaluate(FunctionType ftype, Expression& e0);
Expression Evaluate(FunctionType ftype, Expression& e0, Expression& e1);
Expression Evaluate(FunctionType ftype, Expression& e0, Expression& e1,
                    Expression& e2);
Expression Evaluate(FunctionType ftype, std::vector<Expression>& v);
