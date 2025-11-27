# backend/pagerank.py
import json

DAMPING = 0.85
ITERATIONS = 30

def load_graph(path="data/similarity.json"):
    with open(path, "r") as f:
        return json.load(f)  # { bookA: { bookB: weight } }


def compute_pagerank(graph):
    nodes = list(graph.keys())
    N = len(nodes)

    # Initialize PR
    pr = {n: 1 / N for n in nodes}

    # Precompute outdegree
    outdeg = {n: len(graph[n]) for n in nodes}

    for _ in range(ITERATIONS):
        new_pr = {}
        for node in nodes:
            score = (1 - DAMPING) / N
            # incoming links
            for src in nodes:
                if node in graph[src] and outdeg[src] > 0:
                    score += DAMPING * (pr[src] / outdeg[src])
            new_pr[node] = score
        pr = new_pr
    return pr


def save_pagerank(pr, path="data/pagerank.json"):
    with open(path, "w") as f:
        json.dump(pr, f, indent=2)


if __name__ == "__main__":
    save_pagerank(compute_pagerank(load_graph()))
