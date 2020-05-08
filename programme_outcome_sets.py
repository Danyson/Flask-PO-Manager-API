from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api,reqparse
from meta import metadata




from utils import (
	programme_outcome_set_to_dict,
	can_delete_programme_outcome_set,
)

from programme import ProgrammeOutcomeSet,ProgrammeOutcome





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UECRUD.db'
db = SQLAlchemy(app, metadata=metadata)
api = Api(app)




#*********************Programme Outcome Sets Api Starts***************************

class GetProgrammeOutcomeSets(Resource):
	def get(self):
		result = []
		po_sets = db.session.query(ProgrammeOutcomeSet)
		for po_set in po_sets:
			di = programme_outcome_set_to_dict(po_set)
			di['po_count'] = po_set.programme_outcomes.count()
			di['can_delete'] = can_delete_programme_outcome_set(db.session, po_set)
			result.append(di)
		return {'type': 'programme_outcome_set_list','result': result}
# curl cmd example:curl http://localhost:5000//ui/programme_outcome_manager/programme_outcome_sets  -X GET


class AddProgrammeOutcomeSet(Resource):
	def post(self):
		#errors = request.errors
		data={}
		data= request.json
		name = data['name']
		#po_set = ProgrammeOutcomeSet.by_name(name)
		#if po_set is not None:
			#errors.add("body", "name", "Name already in use")
			#errors.status = HTTPBadRequest.code
			#return
		po_set = ProgrammeOutcomeSet()
		po_set.name = name
		db.session.add(po_set)
		db.session.commit()
#curl cmd example->curl -d '{"name":"h"}' -H "Content-Type: application/json" -X POST http://localhost:5000/ui/programme_outcome_manager/programme_outcome_sets


class EditProgrammeOutcomeSet(Resource):
	def put(self,po_set_id):
		#dbsession = request.dbsession
		#errors = request.errors

		#data = request.validated
		data= request.json
		po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
		#if po_set is None:
		#    err_msg = "Programme Outcome set ({}) not found".format(po_set_id)
		#    errors.add("body", "name", err_msg)
		#    errors.status = HTTPBadRequest.code
		#    return

		name = data['name']
		#if name == po_set.name:
		#    err_msg = "Programme Outcome set ({}) already has name ({})"
		#    errors.add("body", "name", err_msg.format(po_set_id, name))
		#    errors.status = HTTPBadRequest.code
		#    return

		#record = ProgrammeOutcomeSet.by_name(dbsession, name)
		#if record is not None:
		#    errors.add("body", "name", "Name ({}) already in use".format(name))
		#    errors.status = HTTPBadRequest.code
		#    return

		po_set.name = name
		db.session.commit()
#curl example -> curl -d '{"name":"h"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/5 -X PUT


class DeleteProgrammeOutcomeSet(Resource):
	def delete(self,po_set_id):
		#errors = request.errors

		#data = request.validated
		po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
		#if po_set is None:
		#	err_msg = "Programme Outcome set ({}) not found".format(po_set_id)
		#	errors.add("path", "id", err_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		#if can_delete_programme_outcome_set(dbsession, po_set) is False:
		#	err_msg = "Programme Outcome set ({}) in use".format(po_set_id)
		#	errors.add("path", "id", err_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		for po in po_set.programme_outcomes:
			db.session.delete(po)
		db.session.delete(po_set)
		db.session.commit()
#curl example -> curl http://localhost:5000/ui/programme_outcome_manager/programme_outcome_set/8  -X DELETE

#*********************Programme Outcome Sets Api Ends***************************


#************************Programme Outcome Api Ends*****************************


class GetProgrammeOutcome(Resource):
	def get(self,po_id):
		#errors = request.errors
		po = ProgrammeOutcome.by_id(db.session, po_id)
		#if po is None:
			#error_msg = 'Programme Outcome ({}) does not exist'.format(po_id)
			#errors.add('path', 'po_id', error_msg)
			#errors.status = HTTPBadRequest.code
			#return

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


api.add_resource(GetProgrammeOutcomeSets,'/ui/programme_outcome_manager/programme_outcome_sets')
api.add_resource(AddProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_sets')
api.add_resource(EditProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_set/<po_set_id>')
api.add_resource(DeleteProgrammeOutcomeSet,'/ui/programme_outcome_manager/programme_outcome_set/<po_set_id>')
api.add_resource(GetProgrammeOutcome,'/ui/programme_outcome_manager/programme_outcome/<po_id>')




if __name__ == '__main__':
	app.run(debug=True)
