unsigned long __stdcall et_FindToken (unsigned char *pid, int *count);
unsigned long __stdcall et_OpenToken (void **hHandle, unsigned char *pid, int index);
unsigned long __stdcall et_GetSN (void *hHandle, unsigned char *pucSN);
unsigned long __stdcall et_CloseToken (void *hHandle);

char *et_init (void);
