from flask import Flask, render_template, request, jsonify, session, g, current_app
from flask_session import Session
from flask_caching import Cache
from datetime import datetime, timedelta
import json 
import os
import logging
from GraphProcessor import GraphProcessor
from DatabaseHandler import DatabaseHandler

user_configurations = ['end_datetime', 'start_datetime', 'selected_service_id',
                        'in_depth_limit', 'out_depth_limit', 'included_status_codes',
                          'merge_status_codes', 'show_complete_graph', 'filtered_out_nodes', 'graph']
visual_configurations = ['selected_service_id', 'in_depth_limit', 'out_depth_limit',
                          'included_status_codes', 'merge_status_codes', 'show_complete_graph', 'filtered_out_nodes']
#=============== FLASK SETUP 
server = Flask(__name__)

#=============== LOGGING
# Configure logging
logging.basicConfig(level=logging.DEBUG)  
# Create a file handler and set the log file name
log_file_name = 'app.log'
file_handler = logging.FileHandler(log_file_name)
# Configure the format of log messages (optional)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
#END=============== LOGGING

#=============== FLASK SETUP 
with server.open_resource('../Database/config.json') as config_file:
    config = json.load(config_file)
server.config['SESSION_TYPE'] = 'filesystem'
server.config['SECRET_KEY'] = os.urandom(24)
server.config['DEBUG'] = True
server.config['DB_CONFIG'] = config['database']
Session(server)
cache = Cache(server, config={'CACHE_TYPE': 'simple'})
#END=============== FLASK SETUP 

#=============== Cache things
def get_seconds_until_midnight():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return (midnight - now).seconds

def unique_cache_key(*args, **kwargs):
    """Generates a unique cache key for a function."""
    return current_app.name + request.path + request.method + str(hash(frozenset(request.args.items())))

@cache.cached(timeout=get_seconds_until_midnight(), key_prefix='get_min_datetime')
def get_min_datetime():
    return g.db_handler.get_min_datetime()

# caching max date for the rest of the day
@cache.cached(timeout=get_seconds_until_midnight(), key_prefix='get_max_datetime')
def get_max_datetime():
    return g.db_handler.get_max_datetime()

# caching services names for 1 hour
@cache.cached(timeout=3600, key_prefix='get_service_dictionary')  
def get_service_dictionary():
    return g.db_handler.get_services()
 
def get_service_inverted_dictionary():
    original_dictionary = get_service_dictionary()
    inverted_dictionary = {value: key for key, value in original_dictionary.items()}
    return inverted_dictionary

def get_service_id(serviceName):
    return get_service_inverted_dictionary()[serviceName]
#END=============== Cache things

#=============== Session things
@server.before_request
def load_db_handler():
    g.db_handler = DatabaseHandler(server.config['DB_CONFIG'])

def get_default_value(user_config):
    if user_config == 'end_datetime':
        return get_max_datetime()
    if user_config == 'start_datetime':
        end_datetime = session['end_datetime'] if 'end_datetime' in session else get_max_datetime()
        return max(get_min_datetime(), end_datetime - timedelta(minutes=30)) 
    elif user_config == 'selected_service_id':
        return list(get_service_dictionary())[0]
    elif user_config == 'in_depth_limit':
        return 2
    elif user_config == 'out_depth_limit':
        return 2
    elif user_config == 'included_status_codes':
        return {200}
    elif user_config == 'merge_status_codes':
        return False
    elif user_config == 'graph':
        return GraphProcessor()
    elif user_config == 'show_complete_graph':
        return False
    elif user_config == 'filtered_out_nodes':
        return set()
    else:
        raise(NameError(user_config))

@server.before_request
def load_default_user_config():
    modification = False
    for user_config in user_configurations:
        if user_config not in session:
            session[user_config] = get_default_value(user_config)
            modification = True
    if modification:
        session.modified = True
# END =============== Session things

#=============== Update things
@server.route('/get_graph_new_datetime', methods=['POST'])
def get_graph_new_datetime():
    data = request.json
    start_datetime = datetime.fromisoformat(data.get('startTime'))
    end_datetime = datetime.fromisoformat(data.get('endTime'))
    session['start_datetime'] = start_datetime
    session['end_datetime'] = end_datetime

    requests = g.db_handler.get_requests_between(start_datetime, end_datetime)
    session['graph'].clear_graphs()
    session['graph'].includeEdges(requests)
    session.modified = True

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/get_graph_new_in_depth_limit', methods=['POST'])
def get_graph_new_in_depth_limit():
    data = request.json
    new_in_depth_limit = int(data.get('new_depth_limit'))
    session['in_depth_limit'] = new_in_depth_limit

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)
    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/get_graph_new_out_depth_limit', methods=['POST'])
def get_graph_new_out_depth_limit():
    data = request.json
    new_out_depth_limit = int(data.get('new_depth_limit'))
    session['out_depth_limit'] = new_out_depth_limit

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/get_graph_new_selected_service', methods=['POST'])
def get_graph_new_selected_service():
    data = request.json
    new_selected_service = data.get('newService')
    session['selected_service_id'] = get_service_id(new_selected_service)

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/update_complete_graph_checkbox', methods=['POST'])
def update_complete_graph_checkbox():
    data = request.json
    show_complete_graph = data.get('showCompleteGraph') == 'True'
    session['show_complete_graph'] = show_complete_graph
    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/updated_eliminated_services', methods=['POST'])
def updated_eliminated_services():
    data = request.json
    eliminated_services = data.get('eliminatedServices')
    ids = get_service_inverted_dictionary()
    eliminated_services_ids = set([ids[service_name] for service_name in eliminated_services])
    
    session['filtered_out_nodes'] = eliminated_services_ids
    session.modified = True

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})


@server.route('/get_graph_update_status_code', methods=['POST'])
def get_graph_update_status_code():
    data = request.json
    status_code = int(data.get('statusCode'))
    is_checked = data.get('isChecked')

    if is_checked:
        session['included_status_codes'].add(status_code)
    else:
        session['included_status_codes'].remove(status_code)
    session.modified = True

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)

    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/get_graph_update_merge_status_codes_checkbox', methods=['POST'])
def get_graph_update_merge_status_codes_checkbox():
    data = request.json
    merge_status_codes = data.get('isChecked')
    session['merge_status_codes'] = merge_status_codes
    session.modified = True

    visual_dict = {attr:session[attr] for attr in visual_configurations}
    elements = session['graph'].ToCytoscapeList(get_service_dictionary(), **visual_dict)
    return jsonify({"elements": elements, "style":[{"selector":'edge', "style":{'label':'data(label)'}}]})

@server.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    data = request.json
    selected_algorithm = data.get('algorithm')
    visual_dict = {attr:session[attr] for attr in visual_configurations}
    results = session['graph'].run_algorithm(selected_algorithm, get_service_dictionary(), **visual_dict)
    return jsonify({"results": f'{results}'})

# END =============== Update things
@server.route('/')
def index():
    serviceNames=tuple(get_service_dictionary().values())
    load_default_user_config()
    return render_template('index.html', 
                           min_date=get_min_datetime().date(), 
                           max_date=get_max_datetime().date(), 
                           start_datetime = session['start_datetime'],
                           end_datetime = session['end_datetime'],
                           serviceNames=serviceNames,
                           selected_service = get_service_dictionary()[session['selected_service_id']],
                           in_depth_limit= session['in_depth_limit'],
                           out_depth_limit= session['out_depth_limit'],
                           included_status_codes = session['included_status_codes'],
                           merge_status_codes = session['merge_status_codes']
                           )
if __name__ == '__main__':
    server.run(debug=True)
