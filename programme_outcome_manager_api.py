from flask import Flask, request, jsonify, json
#from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, HTTPException
from programme import ProgrammeOutcomeSet, ProgrammeOutcome
from utils import (
    programme_outcome_set_to_dict,
    programme_outcome_to_dict,
    can_add_programme_outcome,
    can_delete_programme_outcome_set,
    can_delete_programme_outcome,
    custom_exception,
)
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'insert db uri'
#db = SQLAlchemy(app, metadata=metadata)
db_engine = create_engine('insert db uri', pool_size = 20, max_overflow = -1)
session = sessionmaker(bind=db_engine)
api = Api(app)
CORS(app)



#*********************Programme Outcome Sets Api Starts**************
class GetProgrammeOutcomeSets(Resource):
    def get(self):
        result = []
        session_local = session()
        po_sets = session_local.query(ProgrammeOutcomeSet)
        session_local.commit()
        for po_set in po_sets:
            di = programme_outcome_set_to_dict(po_set)
            di['po_count'] = po_set.programme_outcomes.count()
            di['can_delete'] = can_delete_programme_outcome_set(session_local, po_set)
            result.append(di)
        session_local.close()
        return {
                'type': 'programme_outcome_set_list',
                'result': result
                }
# curl cmd example:curl http://localhost:5000//ui/programme_outcome_manager/programme_outcome_sets  -X GET

class GetProgrammeOutcomeSetByName(Resource):
    def get(self,name):
        session_local = session()
        po_set = ProgrammeOutcomeSet.by_name(session_local, name.strip())
        if po_set is None:
            description = "Programme outcome set ({}) not found".format(name)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        return {
                 'type': 'programme_outcome_set',
                 'result': {
                            'id': po_set.id,
                            'name': po_set.name,
                           }
                }
#curl example -> curl -X GET http://localhost:5000//ui/programme_outcome_manager/programme_outcome_set_name/Test

class GetProgrammeOutcomeSetById(Resource):
    def get(self,po_set_id):
        session_local = session()
        po_set = ProgrammeOutcomeSet.by_id(session_local, po_set_id)
        if po_set is None:
            description = "Programme outcome set ({}) not found".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        return {
                'type': 'programme_outcome_set',
                'result': {
                            'id': po_set.id,
                            'name': po_set.name,
                          }
               }

#curl example -> curl -X GET http://localhost:5000//ui/programme_outcome_manager/programme_outcome_set_id/1

class AddProgrammeOutcomeSet(Resource):
    def post(self):
        session_local = session()
        data={}
        data= request.json
        name = data['name']
        po_set = ProgrammeOutcomeSet.by_name(session_local,name) #PO set is queried by name for the purpose of name uniquness check
        if po_set is not None:
            description = "Name already in use"
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        po_set = ProgrammeOutcomeSet()            #fresh instance of PO set database object is created
        po_set.name = name                        #name data assigned to the instance name variable
        session_local.add(po_set)                    #instance data added to the database
        try:
            session_local.commit()                            #new data commited and transaction complete
        except:
            session_local.rollback()
            raise
        finally:
            session_local.close()
#curl cmd example->curl -d '{"name":"h"}' -H "Content-Type: application/json" -X POST http://localhost:5000/ui/programme_outcome_manager/programme_outcome_sets

class EditProgrammeOutcomeSet(Resource):
    def put(self,po_set_id):
        session_local = session()
        data= request.json
        po_set = ProgrammeOutcomeSet.by_id(session_local, po_set_id)
        if po_set is None:
            description = "Programme Outcome set ({}) not found".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response



        name = data['name']
        if name == po_set.name:
            description = "Programme Outcome set ({}) already has name ({})"
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        record = ProgrammeOutcomeSet.by_name(session_local, name)
        if record is not None:
            description = "Name ({}) already in use".format(name)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        po_set.name = name        #name data assigned to the current PO set database instance's name variable
        try:
            session_local.commit()       #changes have been commited and transaction is complete
        except:
            session_local.rollback()
        finally:
            session_local.close()
#curl example -> curl -d '{"name":"h"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/5 -X PUT

class DeleteProgrammeOutcomeSet(Resource):
    def delete(self,po_set_id):
        session_local = session()
        po_set = ProgrammeOutcomeSet.by_id(session_local, po_set_id)
        if po_set is None:
            description = "Programme Outcome set ({}) not found".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response



        if can_delete_programme_outcome_set(session_local, po_set) is False:
            description = "Programme Outcome set ({}) in use".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        for po in po_set.programme_outcomes:
            session_local.delete(po)
        session_local.delete(po_set)
        try:
            session_local.commit()
        except:
            session_local.rollback()
        finally:
            session_local.close()
#curl example -> curl http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/8  -X DELETE
#*********************Programme Outcome Sets Api Ends***************************

#************************Programme Outcome Api starts***************************
class GetProgrammeOutcome(Resource):
    def get(self,po_id):
        session_local = session()
        po = ProgrammeOutcome.by_id(session_local, po_id)
        if po is None:
            description = "Programme Outcome ({}) does not exist".format(po_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        return {
                 'type': 'programme_outcome',
                 'result': {
                             'id': po.id,
                             'number': po.number,
                             'title': po.title,
                             'description': po.description,
                             'po_set_id': po.po_set_id,
                            }
               }
#curl example -> curl -X GET http://localhost:5000/ui/programme_outcome_manager/programme_outcome/1


class GetProgrammeOutcomes(Resource):
    def get(self,po_set_id):
        session_local = session()
        po_set = ProgrammeOutcomeSet.by_id(session_local, po_set_id)
        if po_set is None:
            description = "Programme Outcome Set ({}) does not exist".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        record = session_local.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po_set_id).first()
        max_po = record[0]

        li = []
        for po in sorted(po_set.programme_outcomes):
            di = programme_outcome_to_dict(po)
            if po.number < max_po:
                di['can_delete'] = False
            else:
                di['can_delete'] = can_delete_programme_outcome(session_local, po)
            li.append(di)

        result = {
                     'programme_outcomes': li,
                     'can_add': can_add_programme_outcome(session_local, po_set),
                     'title': po_set.name,

                 }

        return {
                 'type': 'programme_outcome_list',
                 'result': result,
               }
# curl example -> curl -X GET http://localhost:5000/ui/programme_outcome_manager/1/programme_outcomes

class AddProgrammeOutcome(Resource):
    def post(self,po_set_id):
        session_local = session()
        po_set = ProgrammeOutcomeSet.by_id(session_local, po_set_id)
        if po_set is None:
            description = "Programme Outcome Set ({}) does not exist".format(po_set_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        if can_add_programme_outcome(session_local, po_set) is False:
            description= '''Programme Outcome Set ({}) in use.
                            Can't add programme outcome'''
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        data={}
        data = request.json
        number = data['number']
        record = session_local.query(ProgrammeOutcome.id).filter_by(po_set_id=po_set_id, number=number).first()

        if record is not None:
            description = 'Programme Outcome with number ({}) already exists'
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        record = session_local.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po_set_id).first()
        if record[0] is not None:
            max_po = record[0]
        else:
            max_po = 0

        if number != max_po + 1:
            description = "Programme Outcome numbers must be consecutive"
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        po = ProgrammeOutcome()
        po.number = number
        po.title = data['title']
        po.description = data['description']
        po.po_set_id = po_set_id
        session_local.add(po)
        try:
            session_local.commit()
        except:
            session_local.rollback()
        finally:
            session_local.close()
#curl example -> curl -d '{"number":3,"title":"addnew","description":"testing"}' -H "Content-Type: application/json"  http://localhost:5000//ui/programme_outcome_manager/1/programme_outcomes -X POST

class EditProgrammeOutcome(Resource):
    def put(self,po_id):
        session_local = session()
        po = ProgrammeOutcome.by_id(session_local, po_id)

        if po is None:
            description = 'Programme Outcome ({}) does not exist'.format(po_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        data={}
        data = request.json
        po.title = data['title']
        po.description = data['description']
        try:
            session_local.commit()
        except:
            session_local.rollback()
        finally:
            session_local.close()
#curl example -> curl -d '{"title":"add","description":"testing complete"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome/1 -X PUT

class DeleteProgrammeOutcome(Resource):
    def delete(self,po_id):
        session_local = session()
        po = ProgrammeOutcome.by_id(session_local, po_id)

        if po is None:
            description = 'Programme Outcome ({}) does not exist'.format(po_id)
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        record = session_local.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po.po_set_id).first()
        max_po = record[0]

        if po.number != max_po:
            description = 'Only last Programme Outcome can be deleted'
            response = app.response_class(response=json.dumps(description),
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response


        if can_delete_programme_outcome(session_local, po) is False:
            #{"status": "error", "errors": [{"location": "path", "name": "id", "description": "Programme Outcome (25) in use"}]}
            description = "Programme Outcome ({}) in use".format(po_id)
            response = app.response_class(response=None,
                                  status=BadRequest.code,
                                  mimetype='application/json')
            return response

        session_local.delete(po)
        try:
            session_local.commit()
        except:
            session_local.rollback()
        finally:
            session_local.close()
#curl example -> curl http://localhost:5000/ui/programme_outcome_manager/programme_outcome/3 -X DELETE
#************************Programme Outcome Api ends*****************************

#uri of Programme Outcome Set starts here
api.add_resource(GetProgrammeOutcomeSets,'/ui/programme_outcome_manager/programme_outcome_sets')
api.add_resource(GetProgrammeOutcomeSetByName,'/ui/programme_outcome_manager/programme_outcome_set_name/<name>')
api.add_resource(GetProgrammeOutcomeSetById,'/ui/programme_outcome_manager/programme_outcome_set/<po_set_id>')
api.add_resource(AddProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_sets')
api.add_resource(EditProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_set/<po_set_id>')
api.add_resource(DeleteProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_set/<po_set_id>')
#uri of Programme Outcome Set ends here

#uri of Programme Outcome  starts here
api.add_resource(GetProgrammeOutcome,'/ui/programme_outcome_manager/programme_outcome/<po_id>')
api.add_resource(GetProgrammeOutcomes,'/ui/programme_outcome_manager/<po_set_id>/programme_outcomes')
api.add_resource(AddProgrammeOutcome,'/ui/programme_outcome_manager/<po_set_id>/programme_outcomes')
api.add_resource(EditProgrammeOutcome,'/ui/programme_outcome_manager/programme_outcome/<po_id>')
api.add_resource(DeleteProgrammeOutcome,'/ui/programme_outcome_manager/programme_outcome/<po_id>')
#uri of Programme Outcome  ends here


if __name__ == '__main__':
    app.run(debug = True)
