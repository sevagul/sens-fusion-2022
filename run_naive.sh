OUTPUT=${1:-"output/output"}
W_SIZE=${2:-"3"}
N_JOBS=${3:-"0"}
./build/OpenCV_naive_stereo ./data/view0.png ./data/view1.png "$OUTPUT"  -w"$W_SIZE" -j"$N_JOBS" 
