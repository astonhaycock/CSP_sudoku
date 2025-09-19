# Sudoku CSP Solver - Performance Analysis

This document analyzes the performance of different heuristics on 9x9 Sudoku puzzles using constraint satisfaction problem (CSP) solving techniques.

## Overview

The Sudoku puzzle is modeled as a CSP with:
- **Variables**: Each cell in the 9x9 grid (r1c1, r1c2, ..., r9c9)
- **Domains**: Numbers 1-9 for each cell
- **Constraints**: 
  - All different values in each row
  - All different values in each column  
  - All different values in each 3x3 box

## How to Run

```bash
# No heuristic (default order)
python3 run_csp.py 9X9_sudoku_easy.csp

# With MRV heuristic
python3 run_csp.py 9X9_sudoku_easy.csp MVR

# With MRV + Degree heuristic  
python3 run_csp.py 9X9_sudoku_easy.csp MVR+
```

## Performance Results

### Very Hard Sudoku (9X9_sudoku_very_hard.csp)

| Heuristic | Branches | Nodes | Time (seconds) | Solutions Found |
|-----------|----------|-------|----------------|-----------------|
| **No Heuristic** | 800,106 | 440,742 | 130.86 | 415 |
| **MRV** | 167,974 | 114,667 | 16.29 | 415 |
| **MRV+** | 167,974 | 114,667 | 16.34 | 415 |

**Performance Gain**: MRV reduces search by ~75% and time by ~87%

### Easy Sudoku (9X9_sudoku_easy.csp)

| Heuristic | Branches | Nodes | Time (seconds) | Solutions Found |
|-----------|----------|-------|----------------|-----------------|
| **No Heuristic** | 3,129 | 1,236 | 0.66 | 1 |
| **MRV** | 159 | 117 | 0.029 | 1 |
| **MRV+** | 159 | 117 | 0.029 | 1 |

**Performance Gain**: MRV reduces search by ~95% and time by ~96%

### Medium Sudoku (9X9_sudoku_med.csp)

| Heuristic | Branches | Nodes | Time (seconds) | Solutions Found |
|-----------|----------|-------|----------------|-----------------|
| **No Heuristic** | 3,375 | 1,705 | 1.03 | 1 |
| **MRV** | 425 | 321 | 0.079 | 1 |
| **MRV+** | 425 | 321 | 0.078 | 1 |

**Performance Gain**: MRV reduces search by ~87% and time by ~92%

### Hard Sudoku (9X9_sudoku_hard.csp)

| Heuristic | Branches | Nodes | Time (seconds) | Solutions Found |
|-----------|----------|-------|----------------|-----------------|
| **No Heuristic** | 8,930 | 4,760 | 1.26 | 1 |
| **MRV** | 912 | 617 | 0.105 | 1 |
| **MRV+** | 912 | 617 | 0.102 | 1 |

**Performance Gain**: MRV reduces search by ~90% and time by ~92%

## Key Observations

1. **MRV Heuristic is Highly Effective**: Across all difficulty levels, MRV dramatically reduces both the search space and solution time.

2. **MRV+ vs MRV Performance**: In these Sudoku instances, MRV+ shows nearly identical performance to MRV because:
   - Given clues create no ties (each has exactly 1 legal value)
   - The degree heuristic provides minimal additional benefit
   - Both heuristics produce the same variable ordering

3. **Scalability**: The performance improvement from heuristics becomes more pronounced as puzzle difficulty increases.

4. **Multiple Solutions**: The "very hard" puzzle actually has 415 solutions, suggesting it may be under-constrained compared to a proper Sudoku (which should have exactly one solution).

## Conclusion

For Sudoku puzzles, the **MRV heuristic alone** provides excellent performance with minimal computational overhead. The degree tie-breaker (MRV+) offers little additional benefit for this problem domain but may be valuable for other CSP types with more tie scenarios.