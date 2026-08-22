# Data Structures Case Study — Planning Document
## Topic: Food Delivery Order & Rider Dispatch System

This plan is built strictly from your professor's handbook. Anything not explicitly stated in the handbook is labeled **[Recommendation]** rather than presented as a requirement. Two things in your prompt I could not verify from the handbook text you gave me:

- **Part III (detailed rubric breakdown for R1/R2/R3)** is referenced on page 3 ("described in Part III") but its actual content isn't in the pages provided — only the summary marks table is. **Get the full rubric text before you finalize what to prioritize.**
- No historical facts, dates, or company names are asserted anywhere below unless flagged as something you must verify yourselves — per the handbook's sourcing rule.

---

## 0. Does this topic even qualify? (Week-1 gate check)

The handbook's sign-off guidance (Part II) approves a topic only if it has:

- **(a) a traceable history across at least two eras**, and
- **(b) a genuine, non-trivial data-structure problem at its core** — not just "a system that stores data in a list."

**Assessment:** Food ordering/delivery plausibly clears (a) — it has a pre-digital era, an early-online-ordering era, and a real-time app-dispatch era, each researchable with primary sources. It clears (b) cleanly — dispatch-and-routing is structurally the same *class* of problem as the handbook's own Metro example (graph + shortest path), plus a genuine FIFO/priority queue problem. **This is my assessment, not a guarantee of approval** — your professor signs off at Week 1, not me.

**[Recommendation]** Narrow the proposed title so it reads as a DS problem, not an app pitch:
> *"Order Queueing & Rider Dispatch Simulation for a Food Delivery Network"*

Frame it in your Week-1 pitch the same way the handbook frames its own examples — one line, structure-first: *"Model restaurant order queues, rider assignment, and delivery routing as queue/priority-queue/hash-map/graph problems, then measure where naive approaches break down."*

---

## 1. TRACE

### What you're actually researching
Not "the history of food delivery apps" in general — you need enough real history to show the system evolved through **distinct eras**, each changing what the underlying engineering problem was. A defensible era framework:

1. **Pre-digital ordering/delivery** — phone-based ordering, walk-in orders, restaurants running their own delivery staff, or region-specific delivery systems that predate computers entirely (India's Mumbai dabbawala lunch-delivery network is a commonly cited example of a pre-digital delivery logistics system — **verify this yourself against a primary/academic source before using it; don't take my word for it**).
2. **Early online ordering** — websites/call-center aggregators where the *ordering* went digital but *dispatch/routing* was still manual or phone-coordinated.
3. **Real-time app-based dispatch** — GPS location data, live rider tracking, and an actual routing/assignment algorithm deciding who delivers what. This era is why your DS choices (graph + priority queue) are justified — it's when routing became an actual computational problem.

### Sources — handbook rules, applied to this topic
- **Minimum 5 sources total, at most 2 encyclopaedic** (so at most 2 Wikipedia-style sources — the rest need to be primary).
- Good primary-source categories for this specific topic:
  - Company "About/Press/Newsroom" pages for founding dates, expansion milestones, stated order volumes.
  - **IEEE/ACM papers on the Vehicle Routing Problem (VRP) or "last-mile delivery dispatch algorithms"** — these are directly usable in your Model section too, not just Trace, since they justify *why* graph/priority-queue structures are the accepted real-world approach.
  - Government or regulatory sources on gig-economy delivery work, if you touch on how dispatch systems affected riders/labor (optional, only if relevant to your framing).
- **Every date and name needs a primary source.** If you can't source a specific claim (a founding year, a "first company to do X" claim, a specific algorithm a real company uses), **leave it out of the report** — don't approximate it. This is the handbook's rule, stated directly.
- If there's a **contested claim** anywhere (e.g., "who invented app-based food delivery first" type claims often are contested) — the handbook wants you to **present both sides**, not resolve it.

### What I won't do
I'm not going to hand you specific founding dates or "Company X was first to do Y" claims, because I can't verify those against a primary source right now, and the handbook is explicit that unsourced dates don't belong in the report. Assign this research to a real person on your team with a source-collection sheet (source, date/claim it supports, is it primary/encyclopaedic).

---

## 2. MODEL

For each structure: the problem it solves, why it fits, key operations, complexity, and — critically — the **alternative you compare it against**, because the handbook wants complexity *reasoning*, not assertion.

### Hash Map — `order_id` / `rider_id` / `restaurant_id` → object
- **Problem:** You constantly need to pull up "where is order #4521" or "is rider #12 currently busy" while the system runs.
- **Why:** O(1) average lookup/insert/delete vs. scanning a list.
- **Operations:** insert, lookup, update-status, delete-on-completion.
- **Complexity:** O(1) average (all three ops); O(n) worst case (hash collisions) — worth a one-line mention.
- **Alternative to compare against:** an unsorted `list` scanned linearly (O(n) lookup), or a sorted list with binary search (O(log n) lookup, but O(n) insert).
- **Experiment:** exactly the Railway example's structure — generate n orders (n = 10, 100, 1,000, 10,000...), time list-scan lookup vs. dict lookup, find where the gap becomes dramatic.

### Queue (FIFO) — orders waiting at a restaurant's kitchen
- **Problem:** Orders should generally be prepared in the order they arrived.
- **Why:** FIFO is the correct real-world semantic — first ordered, first cooked (barring priority overrides, see below).
- **Operations:** enqueue (new order arrives), dequeue (kitchen starts next order).
- **Complexity:** O(1) with `collections.deque`.
- **Alternative to compare against:** Python `list` used as a queue via `list.pop(0)` — this is **O(n)**, a genuine, measurable mistake people make.
- **Experiment:** enqueue/dequeue n items with `deque` vs. `list.pop(0)`, time it, show the crossover.

### Priority Queue / Min-Heap — urgent orders and/or rider selection
Pick **one genuine use**, don't bolt on both just to look thorough unless you can justify both independently:
- **Order side:** orders that have been waiting past some SLA threshold, or flagged urgent, should jump the queue.
- **Rider side:** when an order needs a rider, you want the *best* available one (nearest, or longest-idle) — not just whichever rider happens to be first in a list.
- **Why a heap:** repeatedly finding the "best" item is O(log n) with a heap vs. O(n) with a linear scan re-done every time.
- **Operations:** push (new urgent order / new idle rider), pop-min (next order to prepare / best rider to assign).
- **Complexity:** O(log n) insert and extract-min.
- **Alternative to compare against:** a plain list, re-scanned for the minimum every time a decision is needed (O(n) per decision) — or a sorted list (O(n) insert, O(1) extract, but insertion cost dominates when riders/orders arrive frequently).
- **Experiment:** as rider pool size grows, time "select best rider" via heap vs. via linear scan.

### Graph — locations (restaurants, riders, customers), roads as edges
- **Problem:** Getting a rider from their current location, to the restaurant, to the customer, requires representing an actual road network — not straight-line distance.
- **Why:** This is a routing problem, and routing problems are graph problems.
- **Operations:** add vertex/edge, **BFS** (fewest road segments — cheap, but assumes each segment costs the same), **Dijkstra** (shortest by actual weight — distance or time).
- **Complexity:** BFS O(V+E); Dijkstra O((V+E) log V) with a heap-based priority queue (this is also a legitimate second, more advanced use of a heap, if you want the Model section to show that the heap concept is reusable, not a one-off).
- **Representation — adjacency list vs. adjacency matrix:** the handbook's own Metro example flags this exact comparison. A city/delivery road network is **sparse** (each intersection connects to a handful of others, not to every other node), so adjacency list should win on memory. This needs to be measured, not asserted.
- **The subtle bug to build in on purpose:** this is directly lifted from the handbook's Metro example, and it applies just as cleanly here — if road segments have different travel times (traffic, distance), **BFS's "fewest hops" route is not the same as the actually-fastest route.** Show this with a concrete example: a 2-hop path that's slower than a 3-hop path. This is one of the strongest, most handbook-aligned things you can put in your Analyse section.

### What to explicitly leave out
No Trie, no BST, no fancy string-search structure — **unless** you're genuinely building a feature that needs it (e.g., restaurant name autocomplete). The handbook is explicit: don't add a structure just to look complicated. If your MVP doesn't have a real search feature, don't add one just to justify a structure.

---

## 3. BUILD

**Scope target:** a working CLI simulation, not a web app, not a GUI, not a real map — matching the handbook's own examples (both are CLI-driven, function-based).

### Suggested module layout
```
models.py        Order, Restaurant, Rider, Customer (simple classes/dataclasses)
order_queue.py    per-restaurant FIFO queue (+ optional priority queue for urgent orders)
registry.py       hash-map lookups: orders / riders / restaurants by id
graph.py          LocationGraph: adjacency list, add_edge, bfs(), dijkstra()
dispatch.py       rider selection (priority queue by distance/idle time)
simulation.py     drives the whole flow, reads input, prints/logs output
experiments/      benchmark scripts + plot generation (matplotlib), separate from the sim itself
README.md         how to install/run — required by the handbook
```

### Inputs
- A road/location network (locations + weighted edges) — can be a hardcoded or JSON/CSV-loaded graph.
- A list of riders with a starting location.
- A stream/batch of incoming orders (customer location, restaurant, timestamp, optional "urgent" flag).

### Outputs
- Per-order log: assigned rider, computed route, estimated time.
- End-of-run summary: orders delivered, average wait time, any orders that failed/were rerouted.
- Raw timing data feeding directly into the Analyse section's plots.

### Order flow (this is your architecture, described as a pipeline)
```
Order created
  → registered in hash map (order_id → Order)
  → enqueued at its restaurant's FIFO queue (or pushed to the priority queue if urgent)
  → kitchen dequeues when ready
  → dispatch selects best idle rider via priority queue (nearest / longest-idle)
  → graph.dijkstra() computes rider → restaurant → customer route
  → rider marked busy; order status updated in hash map
  → on simulated arrival, rider marked idle again, order marked delivered
```

### Rider representation
`Rider(id, current_location, status)` — status is `idle` / `busy`. Idle riders are what your priority queue/dispatch structure selects from.

### Simulating failures (this is what earns you an "Analyse" story, mirroring the Metro example's station closure)
- Randomly remove/block a road edge → confirm the system reroutes instead of crashing.
- Randomly mark a rider offline mid-shift → confirm dispatch skips them and reassigns.
- Optional: simulate a restaurant delay and see how it backs up its queue.

### Minimum working version (MVP)
Hash-map registries + FIFO queue per restaurant + graph (15–20 locations) with **both** BFS and Dijkstra implemented + priority-queue-based nearest-idle-rider assignment + a CLI run over a batch of predefined orders, with a printed log.

### Optional/extra (only if MVP is solid and you have time left)
Urgent-order priority queue, road/rider failure simulation with rerouting, multiple restaurants sharing one rider pool, a simple `networkx`-generated static diagram of the graph for the report (not a live GUI — the handbook explicitly wants you to avoid unnecessary web/GUI work).

---

## 4. ANALYSE

This is worth checking against the handbook again: **"Screenshots of terminal output are not plots."** Every plot needs a real chart with **labeled axes and units**.

### Experiments to run (increase dataset size for each)
| # | Comparison | X-axis | Y-axis | What it proves |
|---|---|---|---|---|
| 1 | List scan vs. hash-map lookup | number of orders (n) | lookup time (ms) | O(n) vs O(1) — where the crossover is |
| 2 | `list.pop(0)` queue vs. `deque` | number of enqueue/dequeue ops | time (ms) | O(n) vs O(1) queue ops |
| 3 | Linear scan vs. heap for "best rider" | number of riders | selection time (ms) | O(n) vs O(log n) per decision |
| 4 | Adjacency list vs. adjacency matrix | number of locations | memory used (KB/MB) | list wins for a sparse road network |
| 5 | BFS route vs. Dijkstra route | — (use a fixed constructed graph) | delivery time of chosen route (min) | BFS's "fewest hops" route is not the fastest once edge weights differ — the exact bug the handbook flags in its own Metro example |

**[Recommendation]** Optional 6th plot: order arrival rate vs. queue backlog over simulated time, to show system throughput under load — nice if you have time, not required to satisfy the handbook.

### Rules to hold yourselves to
- Run the experiments for real. The handbook explicitly says don't suggest fake results — that applies to you too.
- Use consistent hardware/conditions when timing (same machine, warm up before timing if needed, average multiple runs).
- Report units on every axis and every number in the text.

---

## 5. REPORT

### What the handbook actually requires (don't add to this list without reason)
- **Length:** 8–12 pages.
- **Sections corresponding to Trace / Model / Build / Analyse.**
- **A source list.**
- **An AI-use appendix.**
- **Source code:** compiling, running, commented, with a README.
- **Plots:** axes labeled with units; terminal screenshots don't count as plots.
- **Contribution log:** 1 page, signed by all 5 members, submitted with the report.
- **Presentation:** 8 minutes, whole group.
- **Sourcing:** minimum 5 sources, at most 2 encyclopaedic, dates/names verified against primary sources.

The handbook does **not** separately list "Introduction," "Limitations," "Conclusion," or "Complexity Analysis" as mandatory standalone sections — those are common academic-writing conventions, not stated requirements here. Given the tight 8–12 page budget, treat them as optional add-ons, not separate chapters.

### [Recommendation] Practical section structure to fit 8–12 pages
1. **Title / group members** (not counted toward page budget typically — confirm with professor)
2. **Trace** (~2–3 pages) — historical eras, sourced claims only
3. **Model** (~2–3 pages) — each structure: problem / why / operations / complexity / alternative — complexity reasoning belongs *here*, not in a separate chapter
4. **Build** (~2 pages) — architecture, module breakdown, what's MVP vs. optional, how failures are simulated
5. **Analyse** (~2–3 pages) — the 5 plots above, with a short paragraph of discussion under each, closing with a brief synthesis paragraph (this covers "conclusion" without needing its own section)
6. **Source list**
7. **AI-use appendix**

---

## 6. GROUP OF 5 — proposed split

| Student | Primary ownership | Also cross-trained on |
|---|---|---|
| 1 | Trace: history research + source collection sheet | Model (must be able to explain DS complexity table) |
| 2 | Model: DS design + complexity write-up, on paper before coding starts | Analyse plots (should understand what's being measured and why) |
| 3 | Build: `models.py`, `registry.py` (hash map), `order_queue.py` (queue + priority queue) | Graph/dispatch logic |
| 4 | Build: `graph.py` (BFS/Dijkstra), `dispatch.py` (rider selection) | Order/queue logic |
| 5 | Analyse: benchmark scripts, plot generation, report assembly + AI-use appendix | Trace sourcing (helps hit the 5-source minimum) |

Because **all 20 marks are shared with no individual component**, but the presentation explicitly requires anyone to be able to field a question about *any* section — build in a review step in Week 4 where each pair swaps sections and quizzes each other before the actual presentation.

---

## 7. TIMELINE (4 weeks)

The handbook is blunt about Week 1: *"groups that begin coding first invariably write the historical section the night before submission... the entire purpose of pairing research with implementation is lost. Sign-off is checked."* Treat the Week-1 gate as a real deadline, not a formality.

**Week 1** — Finalize and pitch the topic (get it signed off, ideally by mid-week so you have buffer). Start Trace research in parallel. Draft the Model section *on paper* — DS choices + complexity reasoning — since sign-off likely hinges on showing a genuine DS problem, per the guidance criteria.

**Week 2** — Implementation: `models.py`, `registry.py`, `order_queue.py`, `graph.py`, `dispatch.py`. Target: an end-to-end MVP simulation running by end of week, even if rough.

**Week 3** — Testing, add failure simulation (blocked roads / offline riders), build the optional features if time allows, then run the actual timed experiments across the dataset sizes and generate all 5 plots.

**Week 4** — Finish Trace writing with citations checked, assemble the full report, write the AI-use appendix, get the contribution log signed by all 5, rehearse the 8-minute presentation with every member speaking, cross-quiz each other on all sections.

---

## 8. AI-USE RULE — what the handbook actually says

*"AI assistants may be used for explanation, not authorship. Declare use in an appendix and state what for. Declared use carries no penalty. Undeclared use detected during presentation Q&A is treated as uncited copying."*

**Practically:** it's fine to use me to understand the concepts, plan the architecture, and get unstuck debugging — but the code and the report's explanations need to be written and understood by your group, because you'll be individually questioned on any part during the 8-minute presentation. Keep a running note of specifically what you used AI for (e.g., "used to explain heap time-complexity," "used to debug a Dijkstra implementation bug," "used to structure the project plan") — that note becomes your AI-use appendix.

---

## FINAL OUTPUT

### 1. 30-second explanation (for your group)
"We're simulating how a food delivery app assigns orders to riders. Orders sit in a queue, we use a hash map to look them up instantly, a priority queue to pick the best available rider, and a graph of roads to find the actual route — then we measure exactly where the naive version (plain lists, linear scans) breaks down compared to the real data structures."

### 2. 2-minute explanation (for your professor)
"Our system is a scaled-down simulation of food delivery order processing and rider dispatch. We traced how food ordering evolved from phone/in-person ordering to online ordering to real-time app-based dispatch, sourcing that history from primary sources rather than assumption. On the Model side, we use a hash map for O(1) order/rider/restaurant lookup instead of a linear scan, a FIFO queue for kitchen order processing, a min-heap priority queue to select the best available rider instead of rescanning the whole rider pool each time, and a graph — compared as an adjacency list vs. adjacency matrix — to represent the road network, routed with both BFS and Dijkstra. We deliberately expose a real bug: BFS's fewest-hop route isn't the fastest route once road segments have different travel times, which is why we use Dijkstra for the actual dispatch decision. In Build, we implemented this as a Python CLI simulation — no GUI — with failure simulation for blocked roads and offline riders. In Analyse, we benchmarked list vs. hash map, list-queue vs. deque, linear-scan vs. heap rider selection, and adjacency list vs. matrix memory use, across increasing dataset sizes, with all results plotted rather than asserted."

### 3. Architecture
```
Customer
   │  places order
   ▼
Order  ──(hash map registry: order_id → Order)──▶ lookup/status anywhere in the system
   │
   ▼
Restaurant's FIFO Queue  (or Priority Queue if urgent)
   │  dequeued when kitchen is ready
   ▼
Dispatch  ──uses Priority Queue over idle riders (nearest / longest-idle)──▶ selects Rider
   │
   ▼
Graph (adjacency list of locations/roads)
   │  Dijkstra: rider's location → restaurant → customer
   ▼
Route + ETA
   │
   ▼
Delivery  ──▶ rider marked idle again, order marked delivered in hash map
```

### 4. Data Structure + Algorithm table
| Structure/Algorithm | Purpose | Key ops | Complexity |
|---|---|---|---|
| Hash Map | O(1) lookup of order/rider/restaurant by id | insert, lookup, delete | O(1) avg, O(n) worst |
| Queue (deque) | FIFO order processing per restaurant | enqueue, dequeue | O(1) |
| Priority Queue (min-heap) | Select best rider / promote urgent orders | push, pop-min | O(log n) |
| Graph (adjacency list) | Represent road/location network | add edge, traverse | O(V+E) space, sparse-friendly |
| BFS | Fewest-hop route | traversal | O(V+E) |
| Dijkstra | Shortest weighted (time/distance) route | traversal + heap | O((V+E) log V) |

### 5. Checklist (strictly from the handbook)
- [ ] Topic pitched and **signed off in Week 1**
- [ ] Report is 8–12 pages
- [ ] Report has sections corresponding to Trace / Model / Build / Analyse
- [ ] Source list included, **≥5 sources, ≤2 encyclopaedic**
- [ ] Every date/name in the report is traceable to a primary source
- [ ] Contested historical claims presented as a debate, not resolved by assertion
- [ ] AI-use appendix included, stating exactly what AI was used for
- [ ] Source code compiles/runs, is commented, has a README
- [ ] All plots have labeled axes with units (no terminal screenshots)
- [ ] Contribution log: 1 page, **signed by all 5 members**
- [ ] Presentation: 8 minutes, **whole group speaks**, everyone can answer questions on any section
- [ ] Confirm the actual Part III rubric text (R1/R2/R3 sub-criteria) before finalizing priorities — not included in the handbook excerpt you gave me

### 6. Likely viva questions
| Question | Concept you need to nail |
|---|---|
| "Why a hash map instead of a sorted list with binary search?" | O(1) avg vs O(log n) lookup, but also O(1) vs O(n) *insertion* — hash maps win when the dataset keeps growing during runtime |
| "Why not just use a list as your queue?" | `list.pop(0)` is O(n) because everything shifts; `deque` is O(1) at both ends |
| "Why a heap for rider selection instead of just scanning riders each time?" | O(log n) vs O(n) per decision, matters once rider pool is large or decisions happen frequently |
| "Why adjacency list over adjacency matrix?" | Sparse graph — matrix wastes O(V²) space when most location pairs aren't directly connected |
| "Why does BFS give the wrong answer for 'fastest route'?" | BFS counts hops, not weight; a 2-hop path can be slower than a 3-hop path if edge weights differ — this is exactly why Dijkstra is used for the actual dispatch |
| "What happens if a road is blocked or a rider goes offline mid-delivery?" | Explain your failure-simulation logic and how dispatch/routing recomputes |
| "How did you verify your historical claims?" | Name your primary sources per claim, explain why encyclopaedic sources were capped at 2 |
| "What did you use AI for, specifically?" | Be exact — refer to your AI-use appendix, don't improvise in the room |
| "What breaks at a much larger scale?" | Point to your Analyse plots — where each structure's advantage starts, and where it might still degrade (e.g., single-threaded simulation, in-memory-only data) |
