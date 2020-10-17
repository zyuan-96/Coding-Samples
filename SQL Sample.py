'''
Course search engine: search

Zhen Yuan
'''

from math import radians, cos, sin, asin, sqrt, ceil
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')


def select_from_str(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns a
    string of SQL code of SELECT, FROM and ON parts

    Input:
        args_from_ui: a dictionary containing search criteria
    Output:
        se_str: SQL query in which parameters are specified with question marks (?)
                of SELECT, FROM and ON parts
    '''
    # Base case
    select_str = "SELECT courses.dept, courses.course_num, courses.title"
    from_str = " FROM courses"
    on_lst = []
    on_str = ""
    if "terms" in args_from_ui:
        from_str += " JOIN (SELECT catalog_index.course_id AS id FROM catalog_index WHERE word"\
                    " IN (?" + ", ?"* (len(args_from_ui["terms"])-1) + ") GROUP BY catalog_index.course_id"\
                    " HAVING COUNT(course_id) = ?)"
        on_lst.append("courses.course_id = id")
    # if either of the cases occurs, the str would be the same
    if ("day" in args_from_ui) or ("enrollment" in args_from_ui) or ("time_start" in args_from_ui)\
    or ("time_end" in args_from_ui) or ("building_code" in args_from_ui):

        select_str += ", sections.section_num, meeting_patterns.day, meeting_patterns.time_start,"\
                      "meeting_patterns.time_end, sections.enrollment"
        from_str += " JOIN sections JOIN meeting_patterns"
        on_lst.append("sections.course_id = courses.course_id AND sections.meeting_pattern_id = "\
                  "meeting_patterns.meeting_pattern_id")     
    
    # if the building_code occurs (building_code and walking_time always appear together)
    if "building_code" in args_from_ui:

        select_str += ", sections.building_code, walking_time"
        # Subquery is needed to create a new table
        from_str += " JOIN (SELECT a.building_code, b.building_code AS building,"\
                    " time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time FROM"\
                    " (SELECT * FROM gps WHERE building_code = ?) AS a JOIN gps AS b)"
        on_lst.append("sections.building_code = building")    

    # If mutiple tables
    if on_lst:
        # join the strings by AND to a new string
        on_str = " ON " + " AND ".join(on_lst)
    se_str = select_str + from_str + on_str
    
    return se_str

def where_str(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns a
    string of SQL query in which parameters are specified with question marks (?)
    of the WHERE part and a list of values for the parameters (one per ? in the query string)

    Input:
        args_from_ui: a dictionary containing search criteria

    Output:
        wh_str: SQL query in which parameters are specified with question marks (?)
                of the WHERE part
        args: a tuple of values for the parameters (one per ? in the query string)
    '''

    wh_lst = []
    args = []
    wh_str = ""
    # append the WHERE part of query and list of parameters in a certain order
    if "terms" in args_from_ui:
        for word in args_from_ui["terms"]:
            args.append(word)
        args.append(len(args_from_ui["terms"]))
    if "walking_time" in args_from_ui:
        wh_lst.append("walking_time <= ?")
        args.append(args_from_ui["building_code"])
        args.append(args_from_ui["walking_time"])
    if "dept" in args_from_ui:
        wh_lst.append("courses.dept = ?")
        args.append(args_from_ui["dept"])
    if "day" in args_from_ui:
        wh_lst.append("meeting_patterns.day IN (?" + ", ?"* (len(args_from_ui["day"])-1) + ")")
        for d in args_from_ui["day"]:
            args.append(d)
    if "enrollment" in args_from_ui:
        wh_lst.append("sections.enrollment BETWEEN ? AND ?")
        for e in args_from_ui["enrollment"]:
            args.append(e)
    if "time_start" in args_from_ui:
        wh_lst.append("meeting_patterns.time_start >= ?")
        args.append(args_from_ui["time_start"])
    if "time_end" in args_from_ui:
        wh_lst.append("meeting_patterns.time_end <= ?")
        args.append(args_from_ui["time_end"])
    
    # if condition occurs
    if wh_lst:
        # join the strings by AND to a new string
        wh_str = " WHERE " + " AND ".join(wh_lst)
    # Make sure the args could not be changed once created, because the order is important
    tuple_args = tuple(args)
    return wh_str, tuple_args



def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is list of strings
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enrollment is a pair of integers
      - walking_time is an integer
      - building_code ia string
      - terms is a list of strings string: ["quantum", "plato"]

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''

    assert_valid_input(args_from_ui)

    # replace with a list of the attribute names in order and a list
    # of query results.
    
    # if the criterion is empty, then return a tuple of empty list
    if not args_from_ui:
        return ([], [])
    else:
        se_str = select_from_str(args_from_ui)
        wh_str, args = where_str(args_from_ui)
        # merge the string
        q = se_str + wh_str
        # connect to a sqlite3 database and make queries
        conn = sqlite3.connect(DATABASE_FILENAME)
        conn.create_function("time_between", 4, compute_time_between)
        c = conn.cursor()
        r = c.execute(q, args)
        lst = r.fetchall()
        header = get_header(c)
        conn.close()
        return (header,lst)








########### auxiliary functions #################
########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['time_start', 'time_end', 'enrollment', 'dept',
                           'terms', 'day', 'building_code', 'walking_time'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # get both buiding_code and walking_time or neither
    has_building = ("building_code" in args_from_ui and
                    "walking_time" in args_from_ui)
    does_not_have_building = ("building_code" not in args_from_ui and
                              "walking_time" not in args_from_ui)

    assert has_building or does_not_have_building

    assert isinstance(args_from_ui.get("building_code", ""), str)
    assert isinstance(args_from_ui.get("walking_time", 0), int)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("day", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("day", [])])

    assert isinstance(args_from_ui.get("dept", ""), str)

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

    assert isinstance(args_from_ui.get("time_start", 0), int)
    assert args_from_ui.get("time_start", 0) >= 0

    assert isinstance(args_from_ui.get("time_end", 0), int)
    assert args_from_ui.get("time_end", 0) < 2400

    # enrollment is a pair of integers, if it exists
    enrollment_val = args_from_ui.get("enrollment", [0, 0])
    assert isinstance(enrollment_val, (list, tuple))
    assert len(enrollment_val) == 2
    assert all([isinstance(i, int) for i in enrollment_val])
    assert enrollment_val[0] <= enrollment_val[1]


def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
