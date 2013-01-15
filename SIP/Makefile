TARGET = et99.pyd
CFILES = sipet99cmodule.c
OFILES = sipet99cmodule.o
HFILES = sipAPIet99.h
OBJS = et99.o

CC = gcc
CXX = g++
LINK = g++
CPPFLAGS = -DNDEBUG -DUNICODE -DQT_LARGEFILE_SUPPORT -I. -IC:\python27\include
CFLAGS = -O2 -Wall
CXXFLAGS = -O2 -Wall
LFLAGS = -mthreads -Wl,-enable-stdcall-fixup -Wl,-enable-auto-import -Wl,-enable-runtime-pseudo-reloc -shared -Wl,-subsystem,windows -Wl,-s
LIBS = -lFT_ET99_API -lpython27 -LC:\python27\libs -L.

all: $(TARGET)

$(HFILES): $(OBJS)
$(CFILES): $(OBJS)
	sip -c . -b et99.sbf et99.sip

$(OFILES): $(CFILES) $(HFILES)

$(TARGET): $(OFILES) $(OBJS)
	$(LINK) $(LFLAGS) -o $@ $(OFILES) $(OBJS) $(LIBS)

clean:
	@del $(TARGET) $(HFILES) $(OFILES) $(OBJS) $(CFILES) et99.sbf
