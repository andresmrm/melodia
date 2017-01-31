%module ondas
%{
/* Includes the header in the wrapper code */
#include "ondas.h"
%}

/* Parse the header file to generate wrappers */
%include "ondas.h"
