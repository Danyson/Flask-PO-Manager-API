def programme_outcome_to_dict(po):                        #function that assigns values to a dictionary from an object passed as an argument
    di = {
        'id': po.id,
        'number': po.number,
        'description': po.description,
        'po_set_id': po.po_set_id,
    }
    title = po.title
    if title is not None:
        di['title'] = title
    return di                                             # returns id,number,description,po set id and title as dictionary object


def programme_outcome_set_to_dict(po_set):                #function that assigns values to a dictionary from an object passed as an argument
    return {
        'id': po_set.id,
        'name': po_set.name,
    }                                                     # returns id,name as dictionary object

def custom_exception(code,description):                   #http status code and its error description string are passed as arguments to this function
    return {
            "status": code,
            "errors": [{"description": description}]
            }                                             #returns http status code and description as a dictionary object

def can_delete_programme_outcome_set(dbsession, po_set):
    return True


def can_delete_programme_outcome(dbsession, po):
    return False


def can_add_programme_outcome(dbsession, po_set):
    return True
