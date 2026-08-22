# Implementation Guide — Do This With Your Group

This guide explains what each TODO is asking you to implement. It is intentionally written as guidance rather than a completed solution because the supplied handbook says AI may be used for explanation, not authorship.

## 1. registry.py

Use a Python dictionary as the underlying storage.

Required behavior:

- `add(id, item)` stores/replaces an item.
- `get(id)` returns the object or `None` if absent.
- `remove(id)` deletes an item if present.
- `__len__()` returns the number of stored items.
- `values()` returns the stored objects.

Complexity to discuss:

- Average lookup/insert/delete: O(1)
- Worst-case hash-table lookup: O(n)

Compare this with scanning a list of objects by ID.

## 2. order_queue.py

### FIFO queue

Use `collections.deque`.

- `enqueue`: add at the right side.
- `dequeue`: remove from the left side.
- Empty queue should return `None`.

Do not use `list.pop(0)` for the real queue.

### Urgent queue

Only keep this feature if your group can justify it in the Model section. Use `heapq` and a small wrapper so Python never needs to compare `Order` objects directly.

## 3. graph.py

Represent the same road network as an adjacency list internally.

### BFS

Use:

- queue
- visited set
- parent map

Return the reconstructed path with the fewest edges.

### Dijkstra

Use:

- distance dictionary
- parent dictionary
- min-heap
- stale-entry check when popping from the heap

Edge weights must be non-negative. Decide whether the weight represents **minutes** or **distance** and use that meaning consistently in the report and experiments.

### Matrix

Convert the adjacency-list data into an n x n matrix. Use one documented convention for missing edges (for example `float('inf')`).

### Failure simulation

Removing a road should remove the corresponding edge in both directions when `bidirectional=True`.

## 4. dispatch.py

Implement the linear version first. It should:

1. Ignore non-IDLE riders.
2. Compute each eligible rider's weighted route to the restaurant.
3. Keep the rider with the smallest total weight.

Then implement the heap version using the same ranking criterion so both methods return the same rider on the same input.

For `assign_rider_to_order`:

1. Mark rider BUSY.
2. Find rider -> restaurant route.
3. Find restaurant -> customer route.
4. Join the two paths without duplicating the restaurant node.
5. Store route and ETA on the order.
6. Mark order OUT_FOR_DELIVERY.

For `complete_delivery`:

- mark order DELIVERED
- mark rider IDLE
- update rider location to the customer's location

## 5. simulation.py

Build a small deterministic network and create a handful of customers, restaurants, riders and orders.

Recommended output:

```text
Order O101 | Rider R2 | Route A -> B -> C -> D | ETA 9.0 min
Order O102 | Rider R1 | Route ...

Summary
-------
Delivered: 4
Failed: 0
Average ETA: ... min
```

Keep the simulation deterministic while developing. Randomness belongs in benchmark generators, where you can set a random seed.

## 6. Benchmarks

Measure elapsed time with `time.perf_counter()`.

Important experimental principle: compare equivalent operations and keep setup time outside the timed section whenever possible.

For each benchmark:

- print raw measurements
- save a labelled plot
- state what the plot demonstrates
- don't claim a theoretical complexity solely from one timing result

## 7. Tests

Run:

```bash
python -m unittest discover -s tests -v
```

Do not remove tests just because your implementation currently fails them. Fix the implementation and understand why the test exists.
