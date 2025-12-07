CXX = g++
CXXFLAGS = -std=c++11 -O2
TARGET = sleuth
SRC = sleuth.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

run: $(TARGET)
	./$(TARGET) > out.txt

clean:
	rm -f $(TARGET)

.PHONY: all run clean
