#include <stdio.h>
#include <stdlib.h>
#include "et99.h"

char *et_init (void)
{
	unsigned char pid[9] = "FFFFFFFF";
	char *ret = (char *) malloc (17);
	int i;
	int index = 1;
	int count = 0;
	void *hHandle = NULL;

	et_FindToken ((unsigned char *) pid, &count);
	et_OpenToken (&hHandle, (unsigned char *) pid, index);
	et_GetSN (hHandle, (unsigned char *) pid);
	et_CloseToken (hHandle);

	for (i = 0; i < 8; i++)
		sprintf (ret + 2 * i, "%.2x", pid[i]);

	return ret;
}
