import time
import random
from Server import Server
from Client import Client
import matplotlib.pyplot as plt

# Constants
DEFAULT_REQUESTS = 50
DEFAULT_RUNS = 5
BUCKET_CAPACITY = 2
TEST_DB_SIZES = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

def evaluate_oram_performance(block_count: int, access_count: int = DEFAULT_REQUESTS, trials: int = DEFAULT_RUNS):
    """
    Measures average throughput and latency of ORAM access over multiple trials.

    Args:
        block_count (int): Number of data blocks in the ORAM.
        access_count (int): Number of random accesses per trial (default: DEFAULT_REQUESTS).
        trials (int): Number of trials to average over (default: DEFAULT_RUNS).

    Returns:
        tuple: (average_throughput, average_latency)
    """
    tree_depth = (block_count - 1).bit_length()

    cumulative_throughput = 0.0
    cumulative_latency = 0.0

    for _ in range(trials):
        server = Server(tree_depth, BUCKET_CAPACITY)
        client = Client(tree_depth)

        # Populate the ORAM with dummy data
        for block_id in range(block_count):
            client.store_data(server, block_id, f"data_{block_id:04}")

        # Begin access measurement
        t_start = time.time()
        for _ in range(access_count):
            random_block = random.randint(0, block_count - 1)
            client.retrieve_data(server, random_block)
        t_end = time.time()

        elapsed = t_end - t_start
        cumulative_throughput += access_count / elapsed
        cumulative_latency += elapsed / access_count

    avg_throughput = cumulative_throughput / trials
    avg_latency = cumulative_latency / trials

    return avg_throughput, avg_latency


def execute_benchmarks():
    """
    Measures average throughput and latency of ORAM access over multiple trials.

    Args:
        block_count (int): Number of data blocks in the ORAM.
        access_count (int): Number of random accesses per trial (default: DEFAULT_REQUESTS).
        trials (int): Number of trials to average over (default: DEFAULT_RUNS).

    Returns:
        tuple: (average_throughput, average_latency)
    """
    results_summary = []

    print(f"{'Database Size':<15} {'Avg Throughput (req/s)':<25} {'Avg Latency (s/req)'}")
    for db_size in TEST_DB_SIZES:
        throughput, latency = evaluate_oram_performance(db_size)
        results_summary.append((db_size, throughput, latency))
        print(f"{db_size:<15} {throughput:<25.2f} {latency:.6f}")

    return results_summary


def generate_plots(metrics):
    """
    Draw the plots
    """
    sizes = [entry[0] for entry in metrics]
    throughputs = [entry[1] for entry in metrics]
    latencies = [entry[2] for entry in metrics]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, throughputs, marker='o', linestyle='-', color='navy')
    plt.title("ORAM Throughput by Database Size")
    plt.xlabel("Number of Blocks")
    plt.ylabel("Throughput (requests/sec)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("oram_throughput.png")
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(throughputs, latencies, marker='s', linestyle='--', color='darkred')
    plt.title("ORAM Latency vs. Throughput")
    plt.xlabel("Throughput (requests/sec)")
    plt.ylabel("Latency (sec/request)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("oram_latency_vs_throughput.png")
    plt.show()


if __name__ == "__main__":
    benchmark_data = execute_benchmarks()
    generate_plots(benchmark_data)