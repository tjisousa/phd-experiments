"""
Topological Rules
Rules for process topology and structure
"""


class TopologicalRules:
    """Rules for process topology and structure"""
    
    PATH_SYMMETRY_RULE = (
        "For every splitting gateway (one-in, multiple-out), there must be a corresponding "
        "joining gateway (multiple-in, one-out) that merges the paths originating from the splitting gateway. "
        "All paths from a split must eventually converge."
    )
    
    VALID_LOOP_STRUCTURE_RULE = (
        "A loop must be properly structured: it must originate from a gateway, "
        "contain at least one task, and have a clear exit path. "
        "An endless loop without an exit condition is not allowed."
    )
    
    NO_UNREACHABLE_NODES = (
        "All flow objects must be reachable from the Start Event. "
        "There should be no isolated subgraphs or unreachable nodes in the process."
    )
    
    PATH_TO_END = (
        "Every flow object must have at least one path leading to an End Event. "
        "Avoid dead ends where execution cannot reach termination."
    )

