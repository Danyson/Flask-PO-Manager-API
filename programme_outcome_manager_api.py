from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, HTTPException
from meta import metadata
from programme import ProgrammeOutcomeSet, ProgrammeOutcome
from utils import (
    programme_outcome_set_to_dict,
    programme_outcome_to_dict,
    can_add_programme_outcome,
    can_delete_programme_outcome_set,
    can_delete_programme_outcome,
    custom_exception,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UECRUD.db'
db = SQLAlchemy(app, metadata=metadata)
api = Api(app)

#*********************Programme Outcome Sets Api Starts**************
class GetProgrammeOutcomeSets(Resource):
    def get(self):
        result = []
        po_sets = db.session.query(ProgrammeOutcomeSet)
        for po_set in po_sets:
            di = programme_outcome_set_to_dict(po_set)
            di['po_count'] = po_set.programme_outcomes.count()
            di['can_delete'] = can_delete_programme_outcome_set(db.session, po_set)
            result.append(di)
        return {
                'type': 'programme_outcome_set_list',
                'result': result
                }
# curl cmd example:curl http://localhost:5000//ui/programme_outcome_manager/programme_outcome_sets  -X GET

class GetProgrammeOutcomeSetByName(Resource):
    def get(self,name):
        po_set = ProgrammeOutcomeSet.by_name(db.session, name.strip())
        if po_set is None:
            description = "Programme outcome set ({}) not found".format(name)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

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
        po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
        if po_set is None:
            description = "Programme outcome set ({}) not found".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

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
        data={}
        data= request.json
        name = data['name']
        po_set = ProgrammeOutcomeSet.by_name(db.session,name) #PO set is queried by name for the purpose of name uniquness check
        if po_set is not None:
            description = "Name already in use"
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json
        po_set = ProgrammeOutcomeSet()            #fresh instance of PO set database object is created
        po_set.name = name                        #name data assigned to the instance name variable
        db.session.add(po_set)                    #instance data added to the database
        db.session.commit()                       #new data commited and transaction complete
#curl cmd example->curl -d '{"name":"h"}' -H "Content-Type: application/json" -X POST http://localhost:5000/ui/programme_outcome_manager/programme_outcome_sets

class EditProgrammeOutcomeSet(Resource):
    def put(self,po_set_id):
        data= request.json
        po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)                  #PO set database instance is acquired  which is queried as per PO set id to check whether if it exsists or not , to check name is repeated and whether it is already in use
        if po_set is None:
            description = "Programme Outcome set ({}) not found".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json


        name = data['name']
        if name == po_set.name:
            description = "Programme Outcome set ({}) already has name ({})"
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        record = ProgrammeOutcomeSet.by_name(db.session, name)
        if record is not None:
            description = "Name ({}) already in use".format(name)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        po_set.name = name        #name data assigned to the current PO set database instance's name variable
        db.session.commit()       #changes have been commited and transaction is complete
#curl example -> curl -d '{"name":"h"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/5 -X PUT

class DeleteProgrammeOutcomeSet(Resource):
    def delete(self,po_set_id):
        po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
        if po_set is None:
            description = "Programme Outcome set ({}) not found".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json


        if can_delete_programme_outcome_set(db.session, po_set) is False:
            description = "Programme Outcome set ({}) in use".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        for po in po_set.programme_outcomes:
            db.session.delete(po)
        db.session.delete(po_set)
        db.session.commit()
#curl example -> curl http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/8  -X DELETE
#*********************Programme Outcome Sets Api Ends***************************

#************************Programme Outcome Api starts***************************
class GetProgrammeOutcome(Resource):
    def get(self,po_id):
        po = ProgrammeOutcome.by_id(db.session, po_id)
        if po is None:
            description = "Programme Outcome ({}) does not exist".format(po_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json


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
        po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
        if po_set is None:
            description = "Programme Outcome Set ({}) does not exist".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po_set_id).first()
        max_po = record[0]

        li = []
        for po in sorted(po_set.programme_outcomes):
            di = programme_outcome_to_dict(po)
            if po.number < max_po:
                di['can_delete'] = False
            else:
                di['can_delete'] = can_delete_programme_outcome(db.session, po)
            li.append(di)

        result = {
                     'programme_outcomes': li,
                     'can_add': can_add_programme_outcome(db.session, po_set),
                     'title': po_set.name,

                 }

        return {
                 'type': 'programme_outcome_list',
                 'result': result,
               }
# curl example -> curl -X GET http://localhost:5000/ui/programme_outcome_manager/1/programme_outcomes

class AddProgrammeOutcome(Resource):
    def post(self,po_set_id):
        po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
        if po_set is None:
            description = "Programme Outcome Set ({}) does not exist".format(po_set_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        if can_add_programme_outcome(db.session, po_set) is False:
            description= '''Programme Outcome Set ({}) in use.
                            Can't add programme outcome'''
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        data={}
        data = request.json
        number = data['number']
        record = db.session.query(ProgrammeOutcome.id).filter_by(po_set_id=po_set_id, number=number).first()

        if record is not None:
            description = 'Programme Outcome with number ({}) already exists'
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po_set_id).first()
        if record[0] is not None:
            max_po = record[0]
        else:
            max_po = 0

        if number != max_po + 1:
            description = "Programme Outcome numbers must be consecutive"
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        po = ProgrammeOutcome()
        po.number = number
        po.title = data['title']
        po.description = data['description']
        po.po_set_id = po_set_id
        db.session.add(po)
        db.session.commit()
#curl example -> curl -d '{"number":3,"title":"addnew","description":"testing"}' -H "Content-Type: application/json"  http://localhost:5000//ui/programme_outcome_manager/1/programme_outcomes -X POST

class EditProgrammeOutcome(Resource):
    def put(self,po_id):
        po = ProgrammeOutcome.by_id(db.session, po_id)

        if po is None:
            description = 'Programme Outcome ({}) does not exist'.format(po_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        data={}
        data = request.json
        po.title = data['title']
        po.description = data['description']
        db.session.commit()
#curl example -> curl -d '{"title":"add","description":"testing complete"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome/1 -X PUT

class DeleteProgrammeOutcome(Resource):
    def delete(self,po_id):
        po = ProgrammeOutcome.by_id(db.session, po_id)

        if po is None:
            description = 'Programme Outcome ({}) does not exist'.format(po_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(po_set_id=po.po_set_id).first()
        max_po = record[0]

        if po.number != max_po:
            description = 'Only last Programme Outcome can be deleted'
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json

        if can_delete_programme_outcome(db.session, po) is False:
            description = "Programme Outcome ({}) in use".format(po_id)
            response = None
            error = HTTPException(description,response)
            error.code = BadRequest.code
            exception = custom_exception(error.code,error.description)
            exception_in_json = jsonify(exception)
            return exception_in_json
        db.session.delete(po)
        db.session.commit()
#curl example -> curl http://localhost:5000/ui/programme_outcome_manager/programme_outcome/3 -X DELETE
#************************Programme Outcome Api ends*****************************

#uri of Programme Outcome Set starts here
api.add_resource(GetProgrammeOutcomeSets,'/ui/programme_outcome_manager/programme_outcome_sets')
api.add_resource(GetProgrammeOutcomeSetByName,'/ui/programme_outcome_manager/programme_outcome_set_name/<name>')
api.add_resource(GetProgrammeOutcomeSetById,'/ui/programme_outcome_manager/programme_outcome_set_id/<po_set_id>')
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
