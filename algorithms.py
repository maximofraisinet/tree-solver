"""
Search algorithms implemented as generators for animation.
BFS (Breadth-First Search) and DFS (Depth-First Search).
"""

from collections import deque
from typing import Generator, Dict, List, Tuple, Optional


def bfs_generator(
    graph: Dict[str, List[str]],
    start: str,
    goal: str
) -> Generator[Tuple[str, str, Optional[List[str]]], None, None]:
    """
    Breadth-First Search implemented as a generator.
    
    Yields tuples of (action, node, path_so_far) where:
    - action: 'visit' (adding to frontier), 'visited' (already processed),
              'goal_found' (reached the goal)
    - node: the node being acted upon
    - path_so_far: the path from start to this node
    """
    if start not in graph:
        return
    
    visited = {start}
    frontier = deque([(start, [start])])
    
    while frontier:
        current, path = frontier.popleft()
        
        yield ('visit', current, path)
        
        if current == goal:
            yield ('goal_found', current, path)
            return
        
        neighbors = graph.get(current, [])
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                frontier.append((neighbor, new_path))
                yield ('exploring', neighbor, new_path)
        
        yield ('visited', current, path)


def dfs_generator(
    graph: Dict[str, List[str]],
    start: str,
    goal: str
) -> Generator[Tuple[str, str, Optional[List[str]]], None, None]:
    """
    Depth-First Search implemented as a generator.
    
    Yields tuples of (action, node, path_so_far) where:
    - action: 'visit', 'visited', 'goal_found'
    - node: the node being acted upon
    - path_so_far: the path from start to this node
    """
    if start not in graph:
        return
    
    visited = set()
    
    def dfs_recursive(node: str, path: List[str]):
        visited.add(node)
        yield ('visit', node, path)
        
        if node == goal:
            yield ('goal_found', node, path)
            return
        
        neighbors = graph.get(node, [])
        for neighbor in neighbors:
            if neighbor not in visited:
                yield ('exploring', neighbor, path + [neighbor])
                yield from dfs_recursive(neighbor, path + [neighbor])
        
        yield ('visited', node, path)
    
    yield from dfs_recursive(start, [start])
