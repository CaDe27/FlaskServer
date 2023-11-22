import networkx as nx
import random as rand
import logging
from collections import deque

logger = logging.getLogger(__name__)
log_file_name = 'app.log'
file_handler = logging.FileHandler(log_file_name)
# Configure the format of log messages (optional)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

def sum(x, y): 
    return x+y

class GraphProcessor:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.reverse_graph = nx.MultiDiGraph()
        self.aggregator = sum

    def clear_graphs(self):
        self.graph.clear()
        self.reverse_graph.clear()

    def update_or_set_edge(self, source, destination, status_code, weight):
        if source in self.graph and destination in self.graph[source] and status_code in self.graph[source][destination]:
            self.graph[source][destination][status_code]['weight'] = self.aggregator(self.graph[source][destination][status_code]['weight'], weight)
            self.reverse_graph[destination][source][status_code]['weight'] = self.aggregator(self.reverse_graph[destination][source][status_code]['weight'], weight)
        else:
            self.graph.add_edge(source, destination, key=status_code, weight=weight)
            self.reverse_graph.add_edge(destination, source, key=status_code, weight=weight)
            
    def includeEdges(self, listOfEdges):
        for edge in listOfEdges:
            statusCodeLevel = edge['status_code']//100 * 100
            self.update_or_set_edge(source=edge['caller_service_id'], destination=edge['receiver_service_id'], status_code=statusCodeLevel, weight=edge['latency_ms'])

    # we pass visited as a parameter because we are doing two bfs's. One for requests coming out
    # and one for requests coming in. The thing is that there might be cycles. If there was one,
    # we wouldn't want to add nodes twice. That's why we have to keep a visited list over both bfs
    # This bfs could be nested to the method that calls it, but I didn't know if that is a good practice          
    
    def ToCytoscapeList(self, serviceName:dict, selected_service_id, in_depth_limit, out_depth_limit, included_status_codes) -> list:
        start_node_id = selected_service_id
        elementList = [{'data': {'id': f'{start_node_id}', 'label': serviceName[start_node_id], 'color':'gray'}}]
        edgeList = []
        visited_edges = set()

        def bfs(start_node_id, graph, depth_limit, reversed):
            queue = deque([(start_node_id, 0)])
            visited_nodes = {start_node_id}
            while queue:
                current_node_id, depth = queue.popleft()
                if current_node_id is not start_node_id:
                    elementList.append({'data': {'id': f'{current_node_id}', 'label': serviceName[current_node_id], 'color':'black'}})
                # If depth limit is reached, do not go further
                if depth != depth_limit and current_node_id in graph:
                    for neighbor in graph[current_node_id]:
                        # Add edge to edges_list
                        for key in graph[current_node_id][neighbor]:
                                #print('key', key)
                                if key in included_status_codes:
                                    if neighbor not in visited_nodes:
                                        visited_nodes.add(neighbor)
                                        queue.append((neighbor, depth + 1))
                                    source = current_node_id if not reversed else neighbor
                                    target = neighbor if not reversed else current_node_id
                                    #print(key, source, target, ((source, target) in visited_edges))
                                    if (key, source, target) not in visited_edges:
                                        visited_edges.add((key, source, target))
                                        edgeList.append(
                                            {'data': 
                                                {'source': f'{source}', 
                                                'target': f'{target}', 
                                                "status_code": key, 
                                                "weight": f'{graph[current_node_id][neighbor][key]["weight"]}'
                                                }
                                            })     
        
        try:
            # Perform BFS traversal and generate node and edge data for Cytoscape
            if self.graph[start_node_id]:
                bfs(start_node_id, graph=self.graph, depth_limit=out_depth_limit, reversed=False)
            if self.reverse_graph[start_node_id]:
                bfs(start_node_id, graph=self.reverse_graph, depth_limit=in_depth_limit, reversed=True)
        except KeyError:
            logger.error(f"Node {start_node_id} is not in the graph.")
            return []
        
        return elementList + edgeList