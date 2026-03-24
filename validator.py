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
    goal_node: Optional[str],
    user_start_node: Optional[str] = None
) -> Tuple[str, str]:
    """
    Validate that the graph forms a valid tree for search.
    
    Args:
        graph: Adjacency list representing the graph
        goal_node: Name of the node marked as goal
        user_start_node: Start node selected by user (optional)
        
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
    
    if user_start_node and user_start_node not in graph:
        raise ValidationError(f"Start node '{user_start_node}' does not exist in the graph.")
    
    start_node = user_start_node
    
    if start_node is None:
        incoming_counts = {node: 0 for node in graph}
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                if neighbor not in incoming_counts:
                    incoming_counts[neighbor] = 1
                else:
                    incoming_counts[neighbor] += 1
        
        start_candidates = [node for node, count in incoming_counts.items() if count == 0]
        
        if len(start_candidates) == 0:
            raise ValidationError("No start node found. There must be at least one node with no incoming edges.")
        
        if len(start_candidates) > 1:
            start_node = start_candidates[0]
        else:
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
    
    def dfs(node: str, path: List[str]) -> Tuple[bool, List[str]]:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                found, cycle = dfs(neighbor, path[:])
                if found:
                    return True, cycle
            elif neighbor in path:
                cycle_start = path.index(neighbor)
                return True, path[cycle_start:] + [neighbor]
        
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
    Build a directed graph representation from scene items.
    Uses the source->target direction from EdgeItems.
    
    Args:
        nodes: List of NodeItem objects
        edges: List of EdgeItem objects
        
    Returns:
        Tuple of (graph adjacency dict, goal_node name)
    """
    node_names = {node.get_name() for node in nodes}
    graph = {name: [] for name in node_names}
    node_by_name = {node.get_name(): node for node in nodes}
    goal_node = None
    
    for node in nodes:
        if node.is_goal_node():
            goal_node = node.get_name()
    
    for edge in edges:
        source = edge.get_source_name()
        target = edge.get_target_name()
        
        if source in graph and target in graph:
            graph[source].append(target)
    
    for node_name in graph:
        node_obj = node_by_name.get(node_name)
        if node_obj:
            neighbors = graph[node_name]
            neighbors.sort(key=lambda n: node_by_name.get(n, node_obj).pos().x())
    
    return graph, goal_node
