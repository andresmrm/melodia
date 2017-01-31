#include "ondas.h"
#include <math.h>
 
PyObject* gerar_onda(double freq, double tempo, double freq_base)
{	
	PyObject* lista = PyList_New(0);
	
	double ampli[3] = {1.0, 1.0, 1.0};
	
	double tam = tempo*freq_base;
	double inst = 0;
	
	int i,j;
	for(i=0; i<tam; i++)
	{
		inst = 0;
		for(j=0; j<3; j++)
		{
			inst += ampli[j] * sin(2 * 3.1415 *  ( i/ (freq_base*(j+1))) * freq ) * 10;
		}
		PyList_Append(lista, PyInt_FromLong(inst*1000));
	}

	return lista;
}
