def programme_outcome_to_dict(po):
    di = {
        'id': po.id,
        'number': po.number,
        'description': po.description,
        'po_set_id': po.po_set_id,
    }
    title = po.title
    if title is not None:
        di['title'] = title
    return di


def programme_outcome_set_to_dict(po_set):
    return {
        'id': po_set.id,
        'name': po_set.name,
    }


def can_delete_programme_outcome_set(dbsession, po_set):
    return True


def can_delete_programme_outcome(dbsession, po):
    return False


def can_add_programme_outcome(dbsession, po_set):
    return True
