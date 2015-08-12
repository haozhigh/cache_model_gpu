CXX_NEW			:= /usr/bin/g++-4.8
CXX_FLAGS		:= -O3 -m64 -std=c++0x -g

BUILD_DIR		:= ../../build
TARGET			:= $(BUILD_DIR)/cachemodel_enhance_histo

all:			$(TARGET)
$(TARGET):		*.cpp *.h
				$(CXX_NEW) $(CXX_FLAGS) *.cpp -o $(TARGET)
				rm -f *.o
