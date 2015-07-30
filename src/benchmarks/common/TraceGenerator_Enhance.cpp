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
#include <string>
#include <string.h>

// Set the maximum amount of threads 
#define MAX_THREADS (8*1024)

//  The LoadAccess class
class LoadAccess {
    public:
    unsigned long addresses[MAX_THREADS];
    unsigned sizes[MAX_THREADS];
    bool valid[MAX_THREADS];
    std::string target;
    unsigned pc;
    bool empty;

    LoadAccess();
};

LoadAccess::LoadAccess() {
    memset(this->addresses, 0, MAX_THREADS * sizeof(unsigned long));
    memset(this->sizes, 0, MAX_THREADS * sizeof(unsigned));
    memset(this->valid, 0, MAX_THREADS * sizeof(bool));
    this->pc = 0;
    this->empty = true;
}

// Record executed kernel names(mangled version)
std::vector<std::string> my_executed_kernels;

//////////////////////////////////
// The trace generator class
//////////////////////////////////
class TraceGenerator : public trace::TraceGenerator {
	
	// Counters
	unsigned long computeCounter;
	unsigned long memoryCounter;
	unsigned kernel_id;
	unsigned threads;
	
	// Status
	bool finished;
	bool initialised;
	
	// File streams
	std::ofstream addrFile;
	
	// Name of the program
	std::string name;
    std::string suite;

    // Last load access
    LoadAccess last_load;
	
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
		float ratio = computeCounter/(float)memoryCounter;
		std::cout << "[Finished kernel] Compute (" << computeCounter << ") memory (" << memoryCounter << ") ratio: " << ratio << "\n";
		//abort(); // End Ocelot. The exit(1) function does not seem to work.
	}
	
	// Open output files
	void initialize(const executive::ExecutableKernel & kernel) {
		std::cout << "Starting with " << kernel.name << "" << std::endl;
		computeCounter = 0;
		memoryCounter = 0;
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

        //  if the same kernel has been executed exit the program
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

        std::string out_dir = "../output/trace_enhance/" + suite + "/" + name;

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
		if( addrFile.is_open()) {
			addrFile.close();
		}
	}
	
	// Ocelot event callback
	void event(const trace::TraceEvent & event) {
		
		// Get a flat thread/block ID/dimension
		unsigned bid = event.blockId.x*event.gridDim.y*event.gridDim.z + event.blockId.y*event.gridDim.z + event.blockId.z;
		unsigned bdim = event.blockDim.x*event.blockDim.y*event.blockDim.z;
		
		// Initialise the trace
		if (!initialised) {
			addrFile << "blocksize: " << event.blockDim.x << " " << event.blockDim.y << " " << event.blockDim.z << std::endl;
			initialised = true;
		}
		
		// Finalise the trace
		if (bid == MAX_THREADS/bdim && !finished) {
			finalise();
		}
		
		// Only process the first MAX_THREADS threads
        if (bid < MAX_THREADS/bdim) {

            // Found a global load
            if ((event.instruction->addressSpace == ir::PTXInstruction::Global &&
                        event.instruction->opcode == ir::PTXInstruction::Ld)
                    ||
                    (event.instruction->opcode == ir::PTXInstruction::Tex )) {

                if (! last_load.empty) {
                    unsigned tid;
                    for (tid = 0; tid < bdim; tid++) {
                        unsigned gid = bid * bdim + tid;
                        if (last_load.valid[gid]) {
                            addrFile << gid << " " << last_load.addresses[gid] << " " << last_load.sizes[gid] << " " << last_load.pc << " " << 0 <<'\n';
                            last_load.valid[gid] = false;
                        }
                    }
                    last_load.empty = true;
                }
                // Loop over a thread block's threads
                unsigned memory_address_counter = 0;
                for (unsigned i = 0; i < bdim; i++) {
                    unsigned gid = bid * bdim + i;

                    unsigned long address;
                    unsigned size;
                    if (event.active[i]) {
                        address = event.memory_addresses[memory_address_counter++];
                        ir::PTXOperand::DataType datatype = event.instruction->type;
                        unsigned vector = event.instruction->vec;
                        size = vector * ir::PTXOperand::bytes(datatype);
                    }
                    else {
                        address = 0;
                        size = 0;
                    }
                    //modified: add PC value info
                    unsigned pc_counter = event.instruction->pc;

                    //Store the info in last_load but not output them now
                    last_load.empty = false;
                    last_load.valid[gid] = true;
                    last_load.pc = pc_counter;
                    last_load.addresses[gid] = address;
                    last_load.sizes[gid] = size;
                    last_load.target = event.instruction->d.toString();
                }
            }
            // else if it is not a global load instruction
            else {
                if (! last_load.empty) {
                    if (last_load.target == event.instruction->a.toString() ||
                            last_load.target == event.instruction->b.toString() ||
                            last_load.target == event.instruction->c.toString()) {
                        unsigned tid;
                        for (tid = 0; tid < bdim; tid++) {
                            unsigned gid = bid * bdim + tid;
                            if (last_load.valid[gid]) {
                                addrFile << gid << " " << last_load.addresses[gid] << " " << last_load.sizes[gid] << " " << last_load.pc << " " << 1 <<'\n';
                                last_load.valid[gid] = false;
                            }
                        }
                        last_load.empty = true;
                    }

                }
            }
        }

        // Count 'compute' and 'memory' instructions to get the 'computational intensity'
        if (event.instruction->addressSpace == ir::PTXInstruction::Global) {
            ir::PTXOperand::DataType datatype = event.instruction->type;
            unsigned size = ir::PTXOperand::bytes(datatype);
            memoryCounter += size;
        }
        else {
            computeCounter++;
        }
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
    original_main(argc - 2,argv + 2);
    return 0;
}

//////////////////////////////////
