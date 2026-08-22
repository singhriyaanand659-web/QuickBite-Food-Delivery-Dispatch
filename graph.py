"""
LocationGraph: represents the road/location network.

The graph uses an adjacency-list representation internally.

BFS = fewest road segments (hops), ignoring edge weight.
Dijkstra = shortest by total travel time using edge weights.

For this project, every edge weight represents estimated travel time
in minutes.

The graph can also be converted into an adjacency matrix for the
memory-comparison experiment.
"""

import heapq
from collections import deque


class LocationGraph:
    def __init__(self):
        # Adjacency list:
        # node -> list of (neighbor, travel_time)
        self._adj: dict[str, list[tuple[str, float]]] = {}

    def add_location(self, name: str) -> None:
        """Add a location (vertex) if it does not already exist."""
        if name not in self._adj:
            self._adj[name] = []

    def add_road(
        self,
        a: str,
        b: str,
        weight: float,
        bidirectional: bool = True
    ) -> None:
        """
        Add a road between two locations.

        `weight` represents estimated travel time in minutes.

        By default, the road is bidirectional.
        """
        if a not in self._adj:
            self.add_location(a)

        if b not in self._adj:
            self.add_location(b)

        self._adj[a].append((b, float(weight)))

        if bidirectional:
            self._adj[b].append((a, float(weight)))

    def neighbors(self, node: str) -> list[tuple[str, float]]:
        """Return [(neighbor, travel_time), ...] for a location."""
        return list(self._adj.get(node, []))

    def bfs_shortest_hops(
        self,
        start: str,
        end: str
    ) -> list[str] | None:
        """
        Return the path with the FEWEST hops from start to end.

        Edge weights are ignored.

        Returns None if the destination is unreachable.
        """
        if start not in self._adj or end not in self._adj:
            return None

        if start == end:
            return [start]

        queue = deque([start])
        visited = {start}

        # parent[child] = node we came from
        parent: dict[str, str | None] = {
            start: None
        }

        while queue:
            current = queue.popleft()

            for neighbor, _ in self._adj[current]:
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                parent[neighbor] = current

                if neighbor == end:
                    return self._reconstruct_path(parent, end)

                queue.append(neighbor)

        return None

    def dijkstra_shortest_weighted(
        self,
        start: str,
        end: str
    ) -> tuple[list[str], float] | None:
        """
        Return (path, total_travel_time) for the shortest weighted path.

        Uses a min-heap priority queue.

        Returns None if the destination is unreachable.
        """
        if start not in self._adj or end not in self._adj:
            return None

        if start == end:
            return ([start], 0.0)

        # distance[node] = best known travel time from start
        distances: dict[str, float] = {
            node: float("inf")
            for node in self._adj
        }

        distances[start] = 0.0

        # parent map for reconstructing the final path
        parent: dict[str, str | None] = {
            start: None
        }

        # Heap entries are:
        # (current_distance, node)
        heap: list[tuple[float, str]] = [
            (0.0, start)
        ]

        while heap:
            current_distance, current = heapq.heappop(heap)

            # Ignore stale heap entries.
            if current_distance > distances[current]:
                continue

            if current == end:
                path = self._reconstruct_path(parent, end)
                return path, current_distance

            for neighbor, weight in self._adj[current]:
                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    parent[neighbor] = current

                    heapq.heappush(
                        heap,
                        (new_distance, neighbor)
                    )

        return None

    def remove_road(
        self,
        a: str,
        b: str,
        bidirectional: bool = True
    ) -> None:
        """Remove a road, optionally in both directions."""

        if a in self._adj:
            self._adj[a] = [
                (neighbor, weight)
                for neighbor, weight in self._adj[a]
                if neighbor != b
            ]

        if bidirectional and b in self._adj:
            self._adj[b] = [
                (neighbor, weight)
                for neighbor, weight in self._adj[b]
                if neighbor != a
            ]

    def to_adjacency_matrix(
        self
    ) -> tuple[list[str], list[list[float]]]:
        """
        Build an adjacency matrix from the current adjacency list.

        Returns:
            (
                node_order,
                matrix
            )

        matrix[i][j] contains the travel time from node i to node j.

        float("inf") means there is no direct road.
        """
        nodes = list(self._adj.keys())
        index = {
            node: i
            for i, node in enumerate(nodes)
        }

        size = len(nodes)

        matrix = [
            [float("inf") for _ in range(size)]
            for _ in range(size)
        ]

        # Distance from a node to itself is zero.
        for i in range(size):
            matrix[i][i] = 0.0

        for source, neighbors in self._adj.items():
            source_index = index[source]

            for destination, weight in neighbors:
                destination_index = index[destination]

                matrix[source_index][destination_index] = weight

        return nodes, matrix

    @staticmethod
    def _reconstruct_path(
        parent: dict[str, str | None],
        end: str
    ) -> list[str]:
        """Reconstruct a path from the parent map."""
        path = []
        current: str | None = end

        while current is not None:
            path.append(current)
            current = parent.get(current)

        path.reverse()
        return path