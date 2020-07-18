#pragma once

#include "function_type.h"
#include "node.h"

void AddToDictionary(unsigned index, Node* node);
Node* GetFromDictionary(unsigned index);
Node* GetFromDictionary(FunctionType ftype);
