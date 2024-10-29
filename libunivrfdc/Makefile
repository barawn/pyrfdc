CFLAGS = -I. -fPIC

TARGET = libunivrfdc.so
SOURCES = $(shell echo metal/*.c *.c) 
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

clean:
	rm -rf *.o
	rm -rf metal/*.o
	rm -rf *.so

$(TARGET): $(OBJECTS)
	$(CC) -shared $(CFLAGS) -o $(TARGET) $(OBJECTS)
	strip --strip-unneeded $(TARGET)

