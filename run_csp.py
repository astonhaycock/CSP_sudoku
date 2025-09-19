from cs4300_csp_parser import parse_cs4300
from cs4300_csp import solve_backtracking, hurrestic
import time



if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python run_csp.py <problem.csp> <var_order>")
        sys.exit(1)
    if len(sys.argv) == 3:
        var_order = sys.argv[2].upper()
    else:
        var_order = "None"
    csp = parse_cs4300(sys.argv[1])
    any_sol = False
    start_time = time.time()
    if var_order == "MVR":
        start_time_hurrestic = time.time()
        var_order = hurrestic(csp, False)
        end_time_hurrestic = time.time()
        print(f"Time taken for hurrestic: {end_time_hurrestic - start_time_hurrestic} seconds")
        for i, sol in enumerate(solve_backtracking(csp, var_order), 1):
            any_sol = True
            print(f"Solution #{i}: {sol}")
    elif var_order == "MVR+":
        var_order = hurrestic(csp, True)
        for i, sol in enumerate(solve_backtracking(csp, var_order), 1):
            any_sol = True
            print(f"Solution #{i}: {sol}")
    else:
        for i, sol in enumerate(solve_backtracking(csp), 1):
            any_sol = True
            print(f"Solution #{i}: {sol}")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    if not any_sol:
        print("No solutions.")
