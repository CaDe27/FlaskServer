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
            
    def includeEdges(self, listOfEdges : list):
        for edge in listOfEdges:
            status_code_block = edge['status_code']//100 * 100
            self.update_or_set_edge(source=edge['caller_service_id'], destination=edge['receiver_service_id'], status_code=status_code_block, weight=edge['latency_ms'])

    def should_skip(self, node_id, visited, filtered_out):
        return node_id in visited or node_id in filtered_out
    
    def bfs(self, start_node_id, graph, depth_limit, included_status_codes,
            merge_status_codes, filtered_out_nodes, 
            visited_edges, visited_nodes, reversed, 
            append_edge_function, append_element_function):
        if self.should_skip(start_node_id, visited_nodes, filtered_out_nodes):
            return
    
        queue = deque([(start_node_id, 0)])
        visited_nodes.add(start_node_id)
        append_element_function(start_node_id)
        while queue:
            current_node_id, depth = queue.popleft()
            if current_node_id in filtered_out_nodes:
                continue
            if current_node_id is not start_node_id:
                append_element_function(current_node_id)
            # If depth limit is reached, do not go further
            if depth != depth_limit and current_node_id in graph:
                for neighbor in graph[current_node_id]:
                    if self.should_skip(neighbor, visited_nodes, filtered_out_nodes):
                        continue

                    # add valid neighbors to queue
                    for status_code in included_status_codes:
                        if status_code in graph[current_node_id][neighbor]:
                            visited_nodes.add(neighbor)
                            queue.append((neighbor, depth + 1))
                    
                    # define beginning and end of the visual edge
                    if reversed:
                        source = neighbor
                        target = current_node_id
                    else:
                        source = current_node_id
                        target = neighbor
                    
                    # Add edge to edges_list
                    if merge_status_codes:
                        edge_exist = False
                        edge_value = 0
                        for status_code in included_status_codes:
                            if status_code in graph[current_node_id][neighbor] and (status_code, source, target) not in visited_edges:
                                visited_edges.add((status_code, source, target))
                                edge_exist = True
                                edge_value = self.aggregator(edge_value, graph[current_node_id][neighbor][status_code]["weight"])
                        if edge_exist:
                            append_edge_function(source, target, status_code=600, weight=edge_value)                      
                    else:      
                        for status_code in included_status_codes:
                            if status_code in graph[current_node_id][neighbor] and (status_code, source, target) not in visited_edges:
                                visited_edges.add((status_code, source, target))
                                append_edge_function(source, target, status_code=status_code, weight=graph[current_node_id][neighbor][status_code]["weight"])
    # we pass visited as a parameter because we are doing two bfs's. One for requests coming out
    # and one for requests coming in. The thing is that there might be cycles. If there was one,
    # we wouldn't want to add nodes twice. That's why we have to keep a visited list over both bfs
    # This bfs could be nested to the method that calls it, but I didn't know if that is a good practice          
    def ToCytoscapeList(self, serviceName:dict, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes) -> list:
        if show_complete_graph:
            central_nodes = tuple(self.graph.nodes)
        else:
            central_nodes = (selected_service_id, )
        elementList = []
        edgeList = []
        visited_edges = set()
        visited_nodes = set()
        def append_edge(source, target, status_code, weight):
            edgeList.append({'data': 
                                {'source': f'{source}', 
                                'target': f'{target}', 
                                "status_code": status_code, 
                                "weight": f'{weight}'
                                }
                            }) 
        for central_node_id in central_nodes:
            if self.should_skip(central_node_id, visited_nodes, filtered_out_nodes):
                continue
            
            start_node_id = central_node_id
            def append_element(node_id):
                color = 'black' if show_complete_graph or node_id is not start_node_id else 'gray'
                elementList.append({'data': {'id': f'{node_id}', 'label': serviceName[node_id], 'color':color}})
            try:
                # Perform BFS traversal and generate node and edge data for Cytoscape
                if self.graph[start_node_id]:
                    self.bfs(start_node_id, graph=self.graph, 
                            depth_limit=out_depth_limit, 
                            included_status_codes=included_status_codes,
                            merge_status_codes=merge_status_codes,
                            filtered_out_nodes=filtered_out_nodes,
                            visited_edges=visited_edges, 
                            visited_nodes=visited_nodes, 
                            reversed=False, 
                            append_edge_function=append_edge, 
                            append_element_function=append_element)
                if self.reverse_graph[start_node_id]:
                    self.bfs(start_node_id, 
                            graph=self.reverse_graph, 
                            depth_limit=in_depth_limit, 
                            included_status_codes=included_status_codes,
                            merge_status_codes=merge_status_codes,
                            filtered_out_nodes=filtered_out_nodes, 
                            visited_edges=visited_edges, 
                            visited_nodes=visited_nodes, 
                            reversed=True, 
                            append_edge_function=append_edge, 
                            append_element_function=append_element)
            except KeyError:
                logger.error(f"An error ocurred when converting to cytoscape list")
                return []
        
        return elementList + edgeList

    def get_visible_graph(self, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes):
        if show_complete_graph:
            central_nodes = tuple(self.graph.nodes)
        else:
            central_nodes = (selected_service_id, )

        visible_graph = nx.MultiDiGraph()
        start_node_id = selected_service_id
        visited_edges = set()
        visited_nodes = set()
        
        for central_node_id in central_nodes:
            if self.should_skip(central_node_id, visited_nodes, filtered_out_nodes):
                continue
            start_node_id = central_node_id
            try:              
                def append_edge(source, target, status_code, weight):
                    visible_graph.add_edge(source, target, key=status_code, weight=weight)
                def append_element(node_id):
                    pass
                # Perform BFS traversal and generate node and edge data for Cytoscape
                if self.graph[start_node_id]:
                    self.bfs(start_node_id, self.graph, out_depth_limit, included_status_codes,
                                merge_status_codes, filtered_out_nodes, visited_edges, visited_nodes=visited_nodes, 
                                reversed=False, append_edge_function=append_edge, append_element_function=append_element)
                if self.reverse_graph[start_node_id]:
                    self.bfs(start_node_id, self.reverse_graph, in_depth_limit, included_status_codes,
                                merge_status_codes, filtered_out_nodes, visited_edges,  visited_nodes=visited_nodes, 
                                reversed=True, append_edge_function=append_edge, append_element_function=append_element)
            except KeyError:
                logger.error(f"An error ocurred when generating the visible graph")
                return []
        return visible_graph

    def run_algorithm(self, selected_algorithm, serviceName:dict, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes):
        graph = self.get_visible_graph(selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes)
        result = ""
        if selected_algorithm == 'Strongly Connected Components':
            scc = nx.strongly_connected_components(graph)
            indx = 0
            for component in scc:
                indx += 1
                result += f"Component {indx}:\n"
                result += "\t"
                for i, id in enumerate(component):
                    result += f"{serviceName[id]}"
                    result += "," if i < len(component)-1 else "\n"
        return result