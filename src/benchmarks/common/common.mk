CUDA_HOME		:= /usr/local/cuda-4.0
CUDA_LIB_PATH	:= $(CUDA_HOME)/lib64
NVCC			:= $(CUDA_HOME)/bin/nvcc
C				:= /usr/bin/gcc-4.4
CXX				:= /usr/bin/g++-4.4

INCLUDE_FLAGS	:= -I./ -I../../common/ -I/usr/local/include/ocelot/api/interface -I/usr/local/cuda-4.0/include
NVCC_FLAGS		:= -O3 -m64 -arch=sm_20 $(INCLUDE_FLAGS)
C_FLAGS			:= -O3 -m64 $(INCLUDE_FLAGS)
CXX_FLAGS		:= -O3 -m64 -std=c++0x $(INCLUDE_FLAGS)

TRACE_GEN_BASE	:= ../../common/TraceGenerator_Base.cpp
MAIN_MACRO_FLAG	:= -Dmain=original_main

BUILD_PATH		:= ../../../../build
TARGET_PROFILER	:= $(BUILD_PATH)/$(TARGET)_profiler
TARGET_SIM		:= $(BUILD_PATH)/$(TARGET)_sim
TARGET_TRACE_BASE	:= $(BUILD_PATH)/$(TARGET)_trace_base

all:				$(TARGET_PROFILER) $(TARGET_TRACE_BASE)

$(TARGET_PROFILER):	$(CU_FILES) $(C_FILES) $(CPP_FILES)
					rm -f *.o
                    ifneq ("$(CU_FILES)", "")
						$(NVCC) -c $(CU_FILES) $(NVCC_FLAGS)
                    endif
                    ifneq ("$(C_FILES)", "")
						$(C) -c $(C_FILES) $(C_FLAGS)
                    endif
                    ifneq ("$(CPP_FILES)", "")
						$(CXX) -c $(CPP_FILES) $(CXX_FLAGS)
                    endif
					$(CXX) -o $(TARGET_PROFILER) *.o $(CXX_FLAGS) -L$(CUDA_LIB_PATH) -Wl,-rpath=$(CUDA_LIB_PATH) -lcudart
					$(CXX) -o $(TARGET_SIM) *.o $(CXX_FLAGS) -L$(CUDA_LIB_PATH) -lcudart
					rm -f *.o

$(TARGET_TRACE_BASE):	$(CU_FILES) $(C_FILES) $(CPP_FILES) $(TRACE_GEN_BASE)
					rm -f *.o
                    ifneq ("$(CU_FILES)", "")
						$(NVCC) -c $(CU_FILES) $(NVCC_FLAGS) $(MAIN_MACRO_FLAG)
                    endif
                    ifneq ("$(C_FILES)", "")
						$(C) -c $(C_FILES) $(C_FLAGS) $(MAIN_MACRO_FLAG)
                    endif
                    ifneq ("$(CPP_FILES)", "")
						$(CXX) -c $(CPP_FILES) $(CXX_FLAGS) $(MAIN_MACRO_FLAG)
                    endif
					$(CXX) -c $(TRACE_GEN_BASE) $(CXX_FLAGS)
					$(CXX) -o $(TARGET_TRACE_BASE) *.o $(CXX_FLAGS) -L$(CUDA_LIB_PATH) `OcelotConfig -l`
					rm -f *.o
