# Python Multithreading vs Multiprocessing
---
This is example repository for blog post at https://www.monterail.com/blog. Below you'll find few examples how to use it.


## Installation
`docker build --tag monte_py .`

## Details
You have few settings you can use while testing different approaches in "Phase 1" and "Phase 2".
- Phase 1: Gathering data
- Phase 2: Generate PDF files
For more detailed Phase 1 & Phase 2 description please go to monterail blog above.

### Availiable settings
- cvs: Number of generated PDF files
- details: Y for detailed report
- p1_type, p2_type: Type for Phase 1/Phase 2 execution. Choices:
  - common: oridinary for loop
  - multithreading
  - multiprocessing
- p1_max_workers, p2_max_workers: Number of paralel threads/processes in multithreading/multiprocessing execution.

### Example usage
- `docker run --rm --name mvm_blog monte_py --cvs=100`: Generates 100 files in common Phase 1 and Phase 2 without dedailed report
- `docker run --rm --name mvm_blog monte_py --cvs=20 --p1_type="multithreading" --p2_type="multiprocessing" --details="Y" --p1_max_workers=8 --p2_max_workers=8`: Generates 20 files with Phase 1 using multithreading approach and Phase 2 using multiprocessing approach. Both phases with 8 workers/processes and with detailed report