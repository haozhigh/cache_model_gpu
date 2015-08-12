//
// == A reuse distance based GPU cache model
// This file is part of a cache model for GPUs. The cache model is based on
// reuse distance theory extended to work with GPUs. The cache model primarly
// focusses on modelling NVIDIA's Fermi architecture.
//
// == More information on the GPU cache model
// Article............A Detailed GPU Cache Model Based on Reuse Distance Theory
// Authors............C. Nugteren et al.
//
// == Contents of this file
// This file provides the Ocelot-based tracer. The tracer takes as input a CUDA
// program emulated in Ocelot and outputs all memory accesses made per thread
// (not in the real execution order - it is just an emulation). The output is
// written to a file and can be limited to a certain amount of threads.
//
// == File details
// Filename...........src/tracer/tracer.cpp
// Author.............Cedric Nugteren <www.cedricnugteren.nl>
// Affiliation........Eindhoven University of Technology, The Netherlands
// Last modified on...30-Oct-2013
//
//////////////////////////////////

// Ocelot includes
#include <ocelot/api/interface/ocelot.h>
#include <ocelot/trace/interface/TraceGenerator.h>
#include <ocelot/trace/interface/TraceEvent.h>
#include <ocelot/executive/interface/ExecutableKernel.h>
#include <ocelot/ir/interface/PTXInstruction.h>
#include <ocelot/ir/interface/PTXOperand.h>

// C++ includes
#include <iostream>
#include <fstream>
#include <map>
#include <stdio.h>
#include <vector>

// Set the maximum amount of threads 
#define MAX_THREADS (8*1024)

// Record executed kernel names(mangled version)
std::vector<std::string> my_executed_kernels;

//////////////////////////////////
// The trace generator class
//////////////////////////////////
class TraceGenerator : public trace::TraceGenerator {
	
	// Counters
	unsigned long loadCounter;
	unsigned long storeCounter;
	unsigned long computeCounter;
	unsigned long memoryCounter;
	unsigned kernel_id;
	unsigned threads;
	
	// Status
	bool finished;
	bool initialised;
	
	// Base address
	unsigned long baseAddress;
	
	// Mapping of CUDA thread IDs (gid) to trace thread IDs (tid)
	std::map<unsigned,unsigned> gids;
	
	// File streams
	std::ofstream addrFile;
	
	// Name of the program
	std::string name;
    std::string suite;

    std::vector<std::string> instructions;
	
	// Public methods
	public:
	
	// Constructor with filename
	TraceGenerator(std::string _name="default", std::string _suite="default") {
		name = _name;
        suite = _suite;
		kernel_id = 0;
	}
	
	// Close output files
	void finish() {
		if (!finished) {
			finalise();
		}
	}
	
	// Open output files
	void initialize(const executive::ExecutableKernel & kernel) {
		std::cout << "Starting with " << kernel.name << "" << std::endl;
		loadCounter = 0;
		storeCounter = 0;
		computeCounter = 0;
		memoryCounter = 0;
		baseAddress = 0;
		threads = 0;
		finished = false;
		initialised = false;

        //  if the same kernel has been executed exit the program
        if (kernel.name == "_Z11corr_kernelPfS_" ||
            kernel.name == "_Z12covar_kernelPfS_" || 
            kernel.name == "_Z26BFS_kernel_multi_blk_inGPUPiS_P4int2S1_S_S_S_S_iiS_S_S_S_") {
            std::cout << "Special kernel: " << kernel.name << std::endl;
            std::cout << "Exiting program..." << std::endl;
            std::_Exit(-1);
        }
        std::vector<std::string>::iterator iter = my_executed_kernels.begin();
        for (; iter != my_executed_kernels.end(); iter++) {
            if ((*iter) == kernel.name) {
                std::cout << "Repeated kernel: " << kernel.name << std::endl;
                std::cout << "Exiting program..." << std::endl;
                std::_Exit(-1);
            }
        }
        my_executed_kernels.push_back(kernel.name);

        char c_str_kernel_id[32];
        sprintf(c_str_kernel_id, "%d", kernel_id);
        std::string str_kernel_id;
        str_kernel_id = c_str_kernel_id;

        std::string out_dir = "../output/trace_code/" + suite + "/" + name;

		if (kernel_id < 10) {
			addrFile.open(out_dir + "/" + name + "_0" + str_kernel_id + ".trc");
		}
		else {
			addrFile.open(out_dir + "/" + name + "_"  + str_kernel_id + ".trc");
		}
		kernel_id++;
	}
	
	// Finalise the data
	void finalise() {
		std::cout << "[Tracer] completed up to " << MAX_THREADS << " threads" << std::endl;
		finished = true;

        for (int i = 0; i < instructions.size(); i++)
            if (instructions[i] != "")
                addrFile << i << " " << instructions[i] << std::endl;
		if( addrFile.is_open()) {
			addrFile.close();
		}
	}
	
	// Ocelot event callback
	void event(const trace::TraceEvent & event) {
        if (event.PC >= instructions.size()) {
            int push_count;
            int i;

            push_count = event.PC - instructions.size() + 1;
            for (i = 0; i < push_count; i++)
                instructions.push_back("");
        }

        if (instructions[event.PC] == "")
            instructions[event.PC] = event.instruction->toString();
	}
};

//////////////////////////////////
// Forward declaration of the original main function
//////////////////////////////////
extern int original_main(int, char**);

//////////////////////////////////
// The new main function to call the Ocelot tracer and the original main
//////////////////////////////////
int main(int argc, char** argv) {
	TraceGenerator generator(argv[2], argv[1]);
	ocelot::addTraceGenerator(generator);
	return original_main(argc - 2,argv + 2);
}

//////////////////////////////////
