CFLAGS = -I. -fPIC

TARGET = libunivrfdc.so
SOURCES = $(shell echo metal/*.c *.c) 
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) -shared $(CFLAGS) -o $(TARGET) $(OBJECTS)
