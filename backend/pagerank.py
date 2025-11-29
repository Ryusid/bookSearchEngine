import json

DAMPING = 0.85
ITERATIONS = 30


def load_graph(path="data/similarity.json"):
    with open(path, "r") as f:
        raw = json.load(f)
    # convert keys to int → cleaner
    return {int(k): {int(n): w for n, w in v.items()} for k, v in raw.items()}


def compute_pagerank(graph):
    nodes = list(graph.keys())
    N = len(nodes)

    pr = {n: 1 / N for n in nodes}
    outdeg = {n: len(graph[n]) for n in nodes}

    for _ in range(ITERATIONS):
        new_pr = {}
        for node in nodes:
            score = (1 - DAMPING) / N
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
    graph = load_graph()
    pr = compute_pagerank(graph)
    save_pagerank(pr)
