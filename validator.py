"""
Tree validation logic.
Checks for valid tree structure: cycles, connectivity, start/goal nodes.
"""

from typing import Dict, List, Set, Optional, Tuple


class ValidationError(Exception):
    """Custom exception for tree validation errors."""
    pass


def validate_tree(
    graph: Dict[str, List[str]],
    goal_node: Optional[str]
) -> Tuple[str, str]:
    """
    Validate that the graph forms a valid tree for search.
    
    Args:
        graph: Adjacency list representing the graph
        goal_node: Name of the node marked as goal
        
    Returns:
        Tuple of (start_node, error_message)
        If valid, error_message is empty string
        
    Raises:
        ValidationError: If the graph is not a valid tree
    """
    if not graph:
        raise ValidationError("The canvas is empty. Add some nodes first.")
    
    if goal_node is None:
        raise ValidationError("No goal node selected. Right-click a node and mark it as Goal.")
    
    if goal_node not in graph:
        raise ValidationError(f"Goal node '{goal_node}' does not exist in the graph.")
    
    incoming_counts = {node: 0 for node in graph}
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in incoming_counts:
                incoming_counts[neighbor] = 1
            else:
                incoming_counts[neighbor] += 1
    
    start_candidates = [node for node, count in incoming_counts.items() if count == 0]
    
    if len(start_candidates) == 0:
        raise ValidationError("No start node found. There must be exactly one node with no incoming edges.")
    
    if len(start_candidates) > 1:
        raise ValidationError(
            f"Multiple start nodes found ({len(start_candidates)} nodes with no incoming edges). "
            "A tree must have exactly one root."
        )
    
    start_node = start_candidates[0]
    
    has_cycle, cycle_path = detect_cycle(graph, start_node)
    if has_cycle:
        raise ValidationError(f"Cycle detected: {' -> '.join(cycle_path)}. Trees cannot have cycles.")
    
    reachable = get_reachable_nodes(graph, start_node)
    unreachable = set(graph.keys()) - reachable
    
    if unreachable:
        unreachable_names = ', '.join(sorted(unreachable))
        raise ValidationError(
            f"Disconnected nodes found: {unreachable_names}. "
            "All nodes must be reachable from the start node."
        )
    
    return start_node, ""


def detect_cycle(graph: Dict[str, List[str]], start: str) -> Tuple[bool, List[str]]:
    """
    Detect if there's a cycle in the graph starting from the given node.
    
    Returns:
        Tuple of (has_cycle, cycle_path)
    """
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str, current_path: List[str]) -> Tuple[bool, List[str]]:
        visited.add(node)
        rec_stack.add(node)
        current_path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, current_path[:]):
                    return True, current_path
            elif neighbor in rec_stack:
                cycle_start = current_path.index(neighbor)
                return True, current_path[cycle_start:] + [neighbor]
        
        rec_stack.remove(node)
        return False, []
    
    return dfs(start, [])


def get_reachable_nodes(graph: Dict[str, List[str]], start: str) -> Set[str]:
    """
    Get all nodes reachable from the start node.
    """
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
    
    return visited


def build_graph_from_scene(nodes: List, edges: List) -> Tuple[Dict[str, List[str]], Optional[str]]:
    """
    Build a graph representation from scene items.
    Auto-determines edge direction based on incoming edge counts.
    
    Args:
        nodes: List of NodeItem objects
        edges: List of EdgeItem objects
        
    Returns:
        Tuple of (graph adjacency dict, goal_node name)
    """
    node_names = {node.get_name() for node in nodes}
    graph = {name: [] for name in node_names}
    goal_node = None
    
    for node in nodes:
        if node.is_goal():
            goal_node = node.get_name()
    
    undirected = {name: set() for name in node_names}
    
    for edge in edges:
        source = edge.get_source_name()
        target = edge.get_target_name()
        
        if source in node_names and target in node_names:
            undirected[source].add(target)
            undirected[target].add(source)
    
    incoming = {name: 0 for name in node_names}
    for node, neighbors in undirected.items():
        for neighbor in neighbors:
            incoming[neighbor] += 1
    
    root_candidates = [n for n, c in incoming.items() if c == 0]
    
    if root_candidates:
        root = root_candidates[0]
        visited = set()
        stack = [root]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in undirected[current]:
                if neighbor not in visited:
                    graph[current].append(neighbor)
                    stack.append(neighbor)
    
    return graph, goal_node
