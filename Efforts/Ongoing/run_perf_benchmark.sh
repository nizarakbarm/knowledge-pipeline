#!/usr/bin/env bash
#===============================================================================
# perf Call Flow Benchmark Script
# Comparing BCC (Runtime C-compilation) vs Python-BPF (AST translation)
# Requires: Python 3.13+, perf, root privileges
#===============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BCC_LOADER="benchmark_bcc.py"
PYBPF_LOADER="benchmark_pythonbpf.py"
TRIGGER_FILE="/tmp/bench_test"
RESULTS_DIR="./perf_results_$(date +%Y%m%d_%H%M%S)"

#===============================================================================
# Helper Functions
#===============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (required for perf)"
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v perf &> /dev/null; then
        log_error "perf not found. Install: apt-get install linux-tools-common"
        exit 1
    fi
    
    if ! python3 --version | grep -E "3\.(1[2-9]|[2-9][0-9])" &> /dev/null; then
        log_warn "Python 3.12+ recommended for PYTHONPERFSUPPORT. Current: $(python3 --version)"
    fi
    
    if [[ ! -f "$BCC_LOADER" ]]; then
        log_error "BCC loader not found: $BCC_LOADER"
        exit 1
    fi
    
    if [[ ! -f "$PYBPF_LOADER" ]]; then
        log_error "Python-BPF loader not found: $PYBPF_LOADER"
        exit 1
    fi
    
    log_success "Dependencies OK"
}

#===============================================================================
# Benchmark Functions
#===============================================================================

run_bcc_benchmark() {
    log_info "Starting BCC benchmark (Native focus)..."
    
    local output_dir="$RESULTS_DIR/bcc"
    mkdir -p "$output_dir"
    
    # Clean up any previous trigger file
    rm -f "$TRIGGER_FILE"
    
    # Terminal 1: Start perf recording
    log_info "Recording BCC with perf (call-graph=fp)..."
    perf record -g --call-graph=fp \
        -e cycles,instructions \
        -o "$output_dir/perf.data" \
        python3 "$BCC_LOADER" &
    
    local bcc_pid=$!
    
    # Terminal 2: Wait, trigger, then stop
    log_info "Waiting 2s for BCC to initialize..."
    sleep 2
    
    log_info "Triggering event: touch $TRIGGER_FILE"
    touch "$TRIGGER_FILE"
    
    log_info "Waiting 1s for event processing..."
    sleep 1
    
    log_info "Stopping BCC (PID: $bcc_pid)..."
    kill -INT $bcc_pid 2>/dev/null || true
    wait $bcc_pid 2>/dev/null || true
    
    # Generate reports
    log_info "Generating BCC reports..."
    perf script -g -i "$output_dir/perf.data" > "$output_dir/callflow.txt" 2>/dev/null || \
        log_warn "perf script failed (data may be empty)"
    
    perf report -g --stdio -i "$output_dir/perf.data" > "$output_dir/report.txt" 2>/dev/null || \
        log_warn "perf report failed"
    
    # Extract key functions
    grep -E "clang::|libbcc|fork|execve|bpf_prog_load" "$output_dir/callflow.txt" > \
        "$output_dir/key_functions.txt" 2>/dev/null || \
        log_warn "No key functions found in BCC profile"
    
    log_success "BCC benchmark complete. Results: $output_dir/"
}

run_pythonbpf_benchmark() {
    log_info "Starting Python-BPF benchmark (Python + Native frames)..."
    
    local output_dir="$RESULTS_DIR/pythonbpf"
    mkdir -p "$output_dir"
    
    # Clean up trigger file
    rm -f "$TRIGGER_FILE"
    
    # Terminal 1: Start perf recording with Python frame support
    log_info "Recording Python-BPF with perf (PYTHONPERFSUPPORT=1, call-graph=lbr)..."
    PYTHONPERFSUPPORT=1 perf record -g --call-graph=lbr \
        -e cycles,instructions \
        -o "$output_dir/perf.data" \
        python3 "$PYBPF_LOADER" &
    
    local pybpf_pid=$!
    
    # Terminal 2: Wait, trigger, then stop
    log_info "Waiting 2s for Python-BPF to initialize..."
    sleep 2
    
    log_info "Triggering event: touch $TRIGGER_FILE"
    touch "$TRIGGER_FILE"
    
    log_info "Waiting 1s for event processing..."
    sleep 1
    
    log_info "Stopping Python-BPF (PID: $pybpf_pid)..."
    kill -INT $pybpf_pid 2>/dev/null || true
    wait $pybpf_pid 2>/dev/null || true
    
    # Generate reports
    log_info "Generating Python-BPF reports..."
    perf script -g -i "$output_dir/perf.data" > "$output_dir/callflow.txt" 2>/dev/null || \
        log_warn "perf script failed (data may be empty)"
    
    perf report -g --stdio -i "$output_dir/perf.data" > "$output_dir/report.txt" 2>/dev/null || \
        log_warn "perf report failed"
    
    # Extract key functions
    grep -E "pythonbpf\.|compile_to_ir|processor|eval_expr|_run_llc|llc|execve" \
        "$output_dir/callflow.txt" > "$output_dir/key_functions.txt" 2>/dev/null || \
        log_warn "No key functions found in Python-BPF profile"
    
    log_success "Python-BPF benchmark complete. Results: $output_dir/"
}

#===============================================================================
# Analysis Functions
#===============================================================================

generate_comparison() {
    log_info "Generating comparison report..."
    
    local report="$RESULTS_DIR/comparison_report.txt"
    
    cat > "$report" << 'EOF'
================================================================================
perf Call Flow Comparison: BCC vs Python-BPF
================================================================================

BCC Key Functions (Expected):
- BPF.__init__
- libbcc.so!bpf_prog_load
- fork()
- execve("/usr/bin/clang")
- clang::driver::Driver::ExecuteCompilation
- clang::FrontendAction::Execute
- LLVMCodeGen

Python-BPF Key Functions (Expected):
- pythonbpf.codegen.BPF.__init__
- pythonbpf.codegen.compile_to_ir
- pythonbpf.codegen.processor
- pythonbpf.vmlinux_parser.vmlinux_proc
- pythonbpf.maps.maps_proc
- pythonbpf.expr.expr_pass.eval_expr
- _handle_attribute_expr
- _handle_name_expr
- pythonbpf.codegen._run_llc
- execve("llc")

================================================================================
EOF
    
    # Append actual findings if available
    if [[ -f "$RESULTS_DIR/bcc/key_functions.txt" ]]; then
        echo -e "\n--- ACTUAL BCC FUNCTIONS ---" >> "$report"
        cat "$RESULTS_DIR/bcc/key_functions.txt" >> "$report"
    fi
    
    if [[ -f "$RESULTS_DIR/pythonbpf/key_functions.txt" ]]; then
        echo -e "\n--- ACTUAL PYTHON-BPF FUNCTIONS ---" >> "$report"
        cat "$RESULTS_DIR/pythonbpf/key_functions.txt" >> "$report"
    fi
    
    log_success "Comparison report: $report"
}

print_next_steps() {
    echo ""
    log_info "Benchmark complete! Next steps:"
    echo ""
    echo "  1. View BCC call flow:"
    echo "     perf report -g --stdio -i $RESULTS_DIR/bcc/perf.data"
    echo ""
    echo "  2. View Python-BPF call flow:"
    echo "     perf report -g --stdio -i $RESULTS_DIR/pythonbpf/perf.data"
    echo ""
    echo "  3. Search for specific functions:"
    echo "     grep 'clang::' $RESULTS_DIR/bcc/callflow.txt"
    echo "     grep 'pythonbpf' $RESULTS_DIR/pythonbpf/callflow.txt"
    echo ""
    echo "  4. View comparison report:"
    echo "     cat $RESULTS_DIR/comparison_report.txt"
    echo ""
    echo "  Results directory: $RESULTS_DIR/"
}

#===============================================================================
# Main
#===============================================================================

main() {
    log_info "perf Call Flow Benchmark"
    log_info "========================"
    
    check_root
    check_dependencies
    
    mkdir -p "$RESULTS_DIR"
    log_info "Results will be saved to: $RESULTS_DIR/"
    
    # Run benchmarks
    run_bcc_benchmark
    echo ""
    run_pythonbpf_benchmark
    echo ""
    
    # Generate comparison
    generate_comparison
    
    # Print next steps
    print_next_steps
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
