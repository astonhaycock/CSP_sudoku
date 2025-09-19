from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable, Iterable, Optional
import operator

Val = int
Assignment = Dict[str, Val]

@dataclass
class CSP:
    domains: Dict[str, List[Val]]
    constraints: List["Constraint"]

@dataclass
class Constraint:
    scope: Tuple[str, ...]
    pred: Callable[[Assignment], bool]
    pretty: str

# ---------- Constraint builders ----------
def c_alldiff(vars: List[str]) -> Constraint:
    def pred(a: Assignment) -> bool:
        vals = [a[v] for v in vars if v in a]
        return len(vals) == len(set(vals))
    return Constraint(tuple(vars), pred, f"alldiff({','.join(vars)})")

def c_bin(op: Callable[[int,int], bool], x: str, y: str, opname: str) -> Constraint:
    def pred(a: Assignment) -> bool:
        if x in a and y in a:
            return op(a[x], a[y])
        return True
    return Constraint((x,y), pred, f"{opname}({x},{y})")

def c_in(x: str, allowed: List[int]) -> Constraint:
    def pred(a: Assignment) -> bool:
        return (x not in a) or (a[x] in allowed)
    return Constraint((x,), pred, f"in({x},{allowed})")

def c_sum(vars: List[str], opstr: str, k: int) -> Constraint:
    opmap = {"==": operator.eq, "!=": operator.ne, "<=": operator.le,
             "<": operator.lt, ">=": operator.ge, ">": operator.gt}
    if opstr not in opmap: raise ValueError(f"bad sum op {opstr}")
    opf = opmap[opstr]
    def pred(a: Assignment) -> bool:
        # Accept partial assignments; only check when fully assigned
        if not all(v in a for v in vars):
            return True
        return opf(sum(a[v] for v in vars), k)
    return Constraint(tuple(vars), pred, f"sum({vars}) {opstr} {k}")

def c_table(vars: List[str], allowed: List[Tuple[int, ...]]) -> Constraint:
    allowed_set = set(tuple(t) for t in allowed)
    def pred(a: Assignment) -> bool:
        if all(v in a for v in vars):
            tup = tuple(a[v] for v in vars)
            return tup in allowed_set
        return True
    return Constraint(tuple(vars), pred, f"table({vars}) allowed {allowed}")

def c_add10(x: str, y: str, cin: str, z: str, cout: str) -> Constraint:
    """Digit-wise base-10 addition: x + y + cin = 10*cout + z, where cin, cout in {0,1} and x,y,z in 0..9.
       Partial assignments are allowed; we only enforce when all involved vars are assigned.
    """
    scope = (x, y, cin, z, cout)
    def pred(a: Assignment) -> bool:
        if all(v in a for v in scope):
            return (a[x] + a[y] + a[cin]) == 10 * a[cout] + a[z]
        return True
    return Constraint(scope, pred, f"add10({x},{y},{cin}->{z},{cout})")


# You must extend the solver by implementing at least one of the following heuristics:

# MRV (Minimum Remaining Values) — choose the variable with the fewest legal values next.

# Degree heuristic — break ties by choosing the variable involved in the most constraints.

# LCV (Least Constraining Value) — when assigning a variable, try values that leave the most flexibility for others.


def consistent_with_local(cons_by_var: Dict[str, List[Constraint]], v: str, a: Assignment) -> bool:
    for c in cons_by_var[v]:
        if not c.pred(a):
            return False
    return True

def hurrestic(csp: CSP, tieBreaker: bool):
    # Copy domains
    domains = {v: list(ds) for v, ds in csp.domains.items()}
    cons_by_var: Dict[str, List[Constraint]] = {v: [] for v in domains}
    assignment: Assignment = {}

    # Track number of consistent values for each variable
    total_possible_moves: Dict[str, int] = {v: 0 for v in domains}

    # Build constraint lookup
    for c in csp.constraints:
        for v in c.scope:
            cons_by_var[v].append(c)

    # Count consistent values for each variable
    for v in domains:
        for val in domains[v]:
            assignment[v] = val
            if consistent_with_local(cons_by_var, v, assignment):
                total_possible_moves[v] += 1
            del assignment[v]

    # Build stats list: (var, legal_values, degree)
    stats = []
    for v in domains:
        legal = total_possible_moves[v]
        degree = len(cons_by_var[v])
        stats.append((v, legal, degree))

    # Manual selection sort style ordering
    ordered = []
    used = set()

    while len(ordered) < len(stats):
        best_var, best_legal, best_degree = None, None, None

        for var, legal, degree in stats:
            if var in used:
                continue

            if best_var is None:
                best_var, best_legal, best_degree = var, legal, degree
            else:
                if tieBreaker:
                    # MRV + Degree tie-break
                    if legal < best_legal or (legal == best_legal and degree > best_degree):
                        best_var, best_legal, best_degree = var, legal, degree
                else:
                    # MRV only
                    if legal < best_legal:
                        best_var, best_legal, best_degree = var, legal, degree

        ordered.append((best_var, best_legal, best_degree))
        used.add(best_var)

    # Extract variable order
    var_order = [var for var, _, _ in ordered]

    # Nicely formatted debug print
    print("Variable ordering:")
    for var, legal, degree in ordered:
        if tieBreaker:
            print(f"  {var}: {legal} legal values, degree {degree}")
        else:
            print(f"  {var}: {legal} legal values")
    print("-" * 30 + "\n")

    return var_order

def print_sudoku(assignment: dict):
    """Pretty print a 9x9 Sudoku assignment dict like {'r1c1': 6, ...}"""
    for r in range(1, 10):
        if r in (4, 7):
            print("-" * 21)  # horizontal separator
        row_vals = []
        for c in range(1, 10):
            if c in (4, 7):
                row_vals.append("|")
            key = f"r{r}c{c}"
            val = assignment.get(key, ".")  # "." if unassigned
            row_vals.append(str(val))
        print(" ".join(row_vals))
    print("\n")

# 
# adding branching factor
# ---------- Simple solver (BT + forward checking) ----------
def solve_backtracking(csp: CSP, var_order: Optional[List[str]]=None) -> Iterable[Assignment]:
    
    domains = {v: list(ds) for v, ds in csp.domains.items()}
    order = var_order or list(domains.keys())
    print(order)
    cons_by_var: Dict[str, List[Constraint]] = {v: [] for v in domains}
    for c in csp.constraints:
        for v in c.scope:
            if v in cons_by_var:
                cons_by_var[v].append(c)

    assignment: Assignment = {}

    def consistent_with_local(v: str, a: Assignment) -> bool:
        for c in cons_by_var[v]:
            if not c.pred(a):
                return False
        return True

    branch_stats = {"branches": 0, "nodes": 0}

    def backtrack(idx: int):
        if idx == len(order):
            yield dict(assignment)
            return
        v = order[idx]

        branch_factor = len(domains[v])
        branch_stats["branches"] += branch_factor
        branch_stats["nodes"] += 1

        for val in domains[v]:
            assignment[v] = val
            if consistent_with_local(v, assignment):
                # forward check
                pruned = []
                ok = True
                for w in order[idx+1:]:
                    removed = []
                    for vv in list(domains[w]):
                        assignment[w] = vv
                        if not consistent_with_local(w, assignment):
                            domains[w].remove(vv); removed.append(vv)
                        del assignment[w]
                    if removed:
                        pruned.append((w, removed))
                    if not domains[w]:
                        ok = False; break
                if ok:
                    yield from backtrack(idx+1)
                # undo pruning
                for w, removed in pruned:
                    domains[w].extend(removed)
            del assignment[v]
   
    yield from backtrack(0)

    print(branch_stats)


