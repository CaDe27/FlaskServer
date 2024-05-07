import numpy as np
import networkx as nx
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

class GraphProcessor:
    implemented_algorithms = ['Degree Centrality', 'Strongly Connected Components', 'Maximum Latency']

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.reverse_graph = nx.MultiDiGraph()

    def clear_graphs(self):
        self.graph.clear()
        self.reverse_graph.clear()

    def update_or_set_edge(self, source, destination, status_code, weight):
        self.graph.add_edge(source, destination, key=status_code, weight=weight)
        self.reverse_graph.add_edge(destination, source, key=status_code, weight=weight)
            
    def includeEdges(self, listOfEdges : list, aggregation_type):
        for edge in listOfEdges:
            status_code_block = edge['status_code']//100 * 100
            self.update_or_set_edge(source=edge['caller_service_id'], destination=edge['receiver_service_id'], status_code=status_code_block, weight=edge['latency_ms'])

    def get_status_code_color(self, status_code):
        if status_code <= 199:
            return 'lightblue'
        elif status_code <= 299:
            return 'green'
        elif status_code <= 399:
            return 'yellow'
        elif status_code <= 499:
            return 'orange'
        elif status_code <= 599:
            return 'red'
        else:
            return 'black'
        
    def get_weight(self, color_weight_list, aggregation_type):
        weights = [cw[1] for cw in color_weight_list]
        if aggregation_type == 'sum latency' or aggregation_type == 'count':
            val = sum(weights)
        elif aggregation_type == 'max latency':
            val = max(weights)
        elif aggregation_type == 'min latency':
            val = min(weights)
        elif aggregation_type == 'average latency':
            val = sum(weights) / len(weights)
        else:
            raise ValueError("Invalid aggregation type")
        return round(val, 1)

    named_colors_to_rgb = {
        "lightblue": (173, 216, 230),
        "green": (0, 128, 0),
        "yellow": (255, 255, 0),
        "orange": (255, 165, 0),
        "red": (255, 0, 0),
        "black": (0, 0, 0)
    }

    def get_color_and_opacity(self, color_weight_list):
        if not color_weight_list:
            return "rgb(0, 0, 0)", 1  # Return opaque black if list is empty

        # Sort by weight
        sorted_list = sorted(color_weight_list, key=lambda x: x[1], reverse=True)
        
        # Extract top two colors and their weights
        top_color, top_weight = sorted_list[0]
        _, second_weight = sorted_list[1] if len(sorted_list) > 1 else (top_color, 0)
        top_weight = float(top_weight)
        second_weight = float(second_weight)

        # Calculate the blend and transparency
        total_weight = top_weight + second_weight
        if total_weight == 0:  # Avoid division by zero
            return "rgb(0, 0, 0)", 1
        
        # Calculate resulting color by blending top two colors
        top_rgb = self.named_colors_to_rgb[top_color]
        
        # Adjust transparency based on dominance
        # More dominance = less transparency. This formula can be adjusted as needed.
        transparency = (top_weight / total_weight) 
        
        return "rgb({0}, {1}, {2})".format(top_rgb[0], top_rgb[1], top_rgb[2]), transparency
    
    def bfs(self, start_node_id, graph, depth_limit, included_status_codes,
            merge_status_codes, filtered_out_nodes,
            aggregation_type, lower_edge_threshold,
            upper_edge_threshold, visited_edges, visited_nodes, 
            reversed, append_edge_function, append_element_function):
        if start_node_id in visited_nodes or start_node_id in filtered_out_nodes:
            return
        
        queue = deque([(start_node_id, 0)])
        enqueued = set()
        visited_nodes.add(start_node_id)
        append_element_function(start_node_id)
        while queue:
            current_node_id, depth = queue.popleft()
            if current_node_id in filtered_out_nodes:
                continue
            if current_node_id is not start_node_id:
                append_element_function(current_node_id)
            # If depth limit is reached, do not go further
            if depth < depth_limit and current_node_id in graph:
                visited_nodes.add(current_node_id)
                for neighbor in graph[current_node_id]:
                    if neighbor in filtered_out_nodes:
                        continue

                    # define beginning and end of the visual edge
                    if reversed:
                        source = neighbor
                        target = current_node_id
                    else:
                        source = current_node_id
                        target = neighbor
                    
                    # Add edge to edges_list
                    if merge_status_codes:
                        count = 0
                        edges_to_merge= list()
                        for status_code in included_status_codes:
                            if status_code in graph[current_node_id][neighbor]:
                                edges_to_merge.append((self.get_status_code_color(status_code), graph[current_node_id][neighbor][status_code]["weight"]))
                        
                        weight = self.get_weight(edges_to_merge, aggregation_type)
                        color, opacity = self.get_color_and_opacity(edges_to_merge)

                        if (len(edges_to_merge) > 0 and lower_edge_threshold <= weight <= upper_edge_threshold):
                            if (600, source, target) not in visited_edges:
                                visited_edges.add((600, source, target))
                                append_edge_function(source, target, status_code=600, weight=weight, color=color, opacity=opacity) 
                            if neighbor not in visited_nodes and neighbor not in enqueued:
                                enqueued.add(neighbor)
                                queue.append((neighbor, depth + 1))
                    else:      
                        for status_code in included_status_codes:
                            if status_code in graph[current_node_id][neighbor]:
                                weight = graph[current_node_id][neighbor][status_code]['weight']
                                if (status_code in graph[current_node_id][neighbor] 
                                    and lower_edge_threshold <=  weight <= upper_edge_threshold):
                                    if (status_code, source, target) not in visited_edges:
                                        visited_edges.add((status_code, source, target))
                                        append_edge_function(source, target, status_code=status_code, weight=round(weight, 1), 
                                                            color=self.get_status_code_color(status_code),
                                                            opacity=1)

                                    if neighbor not in visited_nodes and neighbor not in enqueued:
                                        enqueued.add(neighbor)
                                        queue.append((neighbor, depth + 1))
    # we pass visited as a parameter because we are doing two bfs's. One for requests coming out
    # and one for requests coming in. The thing is that there might be cycles. If there was one,
    # we wouldn't want to add nodes twice. That's why we have to keep a visited list over both bfs
    # This bfs could be nested to the method that calls it, but I didn't know if that is a good practice          
    def ToCytoscapeList(self, service_name:dict, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes,
                        aggregation_type, lower_edge_threshold, 
                        upper_edge_threshold, no_upper_threshold_flag) -> list:
        if len(self.graph.nodes) == 0:
            return
        if show_complete_graph:
            central_nodes = tuple(self.graph.nodes)
        else:
            central_nodes = (selected_service_id, )
        upper_edge_threshold = np.Inf if no_upper_threshold_flag else upper_edge_threshold
        elementList = []
        edgeList = []
        visited_edges = set()
        visited_nodes = set()
        visited_nodes_reversed = set()
        def append_edge(source, target, status_code, weight, color, opacity):
            edgeList.append({'data': 
                                {'source': f'{source}', 
                                'target': f'{target}', 
                                "status_code": status_code, 
                                "weight": f'{weight}',
                                "color": f'{color}',
                                "opacity": f'{opacity}'
                                }
                            }) 
        for central_node_id in central_nodes:
            if central_node_id not in self.graph.nodes:
                continue
            
            if central_node_id in filtered_out_nodes:
                continue
            
            start_node_id = central_node_id
            def append_element(node_id):
                color = 'black' if show_complete_graph or node_id is not start_node_id else 'gray'
                elementList.append({'data': {'id': f'{node_id}', 'label': service_name[node_id], 'color':color}})
            # try:
                # Perform BFS traversal and generate node and edge data for Cytoscape
            if self.graph[start_node_id] and start_node_id not in visited_nodes:
                self.bfs(start_node_id, graph=self.graph, 
                        depth_limit=out_depth_limit, 
                        included_status_codes=included_status_codes,
                        merge_status_codes=merge_status_codes,
                        filtered_out_nodes=filtered_out_nodes,
                        aggregation_type=aggregation_type,
                        lower_edge_threshold=lower_edge_threshold,
                        upper_edge_threshold=upper_edge_threshold,
                        visited_edges=visited_edges, 
                        visited_nodes=visited_nodes, 
                        reversed=False, 
                        append_edge_function=append_edge, 
                        append_element_function=append_element)
            if self.reverse_graph[start_node_id] and start_node_id not in visited_nodes_reversed:
                self.bfs(start_node_id, 
                        graph=self.reverse_graph, 
                        depth_limit=in_depth_limit, 
                        included_status_codes=included_status_codes,
                        merge_status_codes=merge_status_codes,
                        filtered_out_nodes=filtered_out_nodes,
                        aggregation_type=aggregation_type, 
                        lower_edge_threshold=lower_edge_threshold,
                        upper_edge_threshold=upper_edge_threshold,
                        visited_edges=visited_edges, 
                        visited_nodes=visited_nodes_reversed, 
                        reversed=True, 
                        append_edge_function=append_edge, 
                        append_element_function=append_element)
            # except KeyError:
            #     logger.error(f"An error ocurred when converting to cytoscape list")
            #     return []
        
        return elementList + edgeList

    def get_visible_graph(self, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes,
                        aggregation_type, lower_edge_threshold,
                        upper_edge_threshold, no_upper_threshold_flag):
        if show_complete_graph:
            central_nodes = tuple(self.graph.nodes)
        else:
            central_nodes = (selected_service_id, )
        upper_edge_threshold = np.Inf if no_upper_threshold_flag else upper_edge_threshold
        visible_graph = nx.MultiDiGraph()
        start_node_id = selected_service_id
        visited_edges = set()
        visited_nodes = set()
        visited_nodes_reversed = set()
        
        for central_node_id in central_nodes:
            if central_node_id in filtered_out_nodes:
                continue
            start_node_id = central_node_id
            try:              
                def append_edge(source, target, status_code, weight, color, opacity):
                    visible_graph.add_edge(source, target, key=status_code, weight=weight)
                def append_element(node_id):
                    pass
                # Perform BFS traversal and generate node and edge data for Cytoscape
                if self.graph[start_node_id] and start_node_id not in visited_nodes:
                    self.bfs(start_node_id, self.graph, out_depth_limit, included_status_codes,
                                merge_status_codes, filtered_out_nodes, aggregation_type, lower_edge_threshold,
                                upper_edge_threshold, visited_edges, visited_nodes=visited_nodes, 
                                reversed=False, append_edge_function=append_edge, append_element_function=append_element)
                if self.reverse_graph[start_node_id] and start_node_id not in visited_nodes_reversed:
                    self.bfs(start_node_id, self.reverse_graph, in_depth_limit, included_status_codes,
                                merge_status_codes, filtered_out_nodes, aggregation_type, lower_edge_threshold,
                                upper_edge_threshold, visited_edges, visited_nodes=visited_nodes_reversed, 
                                reversed=True, append_edge_function=append_edge, append_element_function=append_element)
            except KeyError:
                logger.error(f"An error ocurred when generating the visible graph")
                return []
        return visible_graph

    def run_algorithm(self, selected_algorithm, service_name:dict, selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes,
                        aggregation_type, lower_edge_threshold,
                        upper_edge_threshold, no_upper_threshold_flag):
        graph = self.get_visible_graph(selected_service_id, 
                        in_depth_limit, out_depth_limit, 
                        included_status_codes, merge_status_codes, 
                        show_complete_graph, filtered_out_nodes, 
                        aggregation_type, lower_edge_threshold,
                        upper_edge_threshold, no_upper_threshold_flag)
        if selected_algorithm == 'Strongly Connected Components':
            result = self.strongly_connected_components(graph, service_name)
        elif selected_algorithm == 'Degree Centrality':
            result = self.degree_centrality(graph, service_name)
        elif selected_algorithm == 'Maximum Latency':
            result = self.maximum_latency(graph, service_name)
        return result
    
    def strongly_connected_components(self, graph, service_name):
        scc = nx.strongly_connected_components(graph)
        indx = 0
        result = ""
        for component in scc:
            indx += 1
            result += f"Component {indx}:\n"
            result += "\t"
            for i, id in enumerate(component):
                result += f"{service_name[id]}"
                result += "," if i < len(component)-1 else "\n"
        return result
    
    def degree_centrality(self, graph, service_name):
        result = ""
        node_centralities = nx.degree_centrality(graph)
        sorted_ids = sorted(node_centralities, key=lambda id: node_centralities[id], reverse=True)
        node_centralities = {id: node_centralities[id] for id in sorted_ids} 

        max_service_name_length = max(len(service_name[index]) for index in service_name)
        for index, centrality in node_centralities.items():
            result += f"Node: {service_name[index]:<{max_service_name_length}}\tcentrality: {centrality:.2f}\n" 
        return result
    
    def maximum_latency(self, graph, service_name):
        condensed = nx.condensation(graph)
        # keys: original graph nodes, values: index of the scc they 
        # belong in the condensed graph
        scc = condensed.graph['mapping']
        for u, v, key, data in graph.edges(data = True, keys = True):
            if scc[u] != scc[v]:
                if 'weight' in condensed[scc[u]][scc[v]]:
                    currentValue = condensed[scc[u]][scc[v]]['weight']
                    condensed[scc[u]][scc[v]]['weight'] = max(data['weight'], currentValue)
                else:
                    condensed[scc[u]][scc[v]]['weight'] = data['weight']
        
        longest_condensed_path = nx.dag_longest_path(condensed, weight='weight')
        result = ""
        total_latency = 0
        for indx in range(1, len(longest_condensed_path)):
            u = longest_condensed_path[indx-1]
            v = longest_condensed_path[indx]
            total_latency += condensed[u][v]['weight']
        result = f"Maximum latency path:\n"
        result += f"\tLatency: {total_latency}\n"
        for indx, scc in enumerate(longest_condensed_path):
            result += f"{indx+1}:"
            for service_id in (condensed.nodes.data())[scc]['members']:
                result += f" {service_name[service_id]}"
            result += "\n"
        return result