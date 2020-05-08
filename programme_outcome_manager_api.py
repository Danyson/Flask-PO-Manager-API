from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


from flask_restful import Resource, Api,reqparse
from meta import metadata




from utils import (
	programme_outcome_set_to_dict,
	programme_outcome_to_dict,
	can_add_programme_outcome,
	can_delete_programme_outcome_set,
	can_delete_programme_outcome,

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

class GetProgrammeOutcomeSetByName(Resource):
	def get(self,name):
		#errors = request.errors
		po_set = ProgrammeOutcomeSet.by_name(db.session, name.strip())
		#if po_set is None:
		#    err_msg = "Programme outcome set ({}) not found".format(name)
		#    errors.add("body", "name", err_msg)
		#    errors.status = HTTPBadRequest.code
		#    return

		return {
			'type': 'programme_outcome_set',
			'result': {
				'id': po_set.id,
				'name': po_set.name,
			}
		}
#curl example -> curl -X GET http://localhost:5000//ui/programme_outcome_manager/programme_outcome_set_id/Test


class GetProgrammeOutcomeSetById(Resource):
	def get(self,po_set_id):
		#errors = request.errors
		po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
		#if po_set is None:
		#    err_msg = "Programme outcome set ({}) not found".format(name)
		#    errors.add("body", "name", err_msg)
		#    errors.status = HTTPBadRequest.code
		#    return

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


#************************Programme Outcome Api starts*****************************


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

class GetProgrammeOutcomes(Resource):
	def get(self,po_set_id):
		#errors = request.errors
		po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
		#if po_set is None:
		#	error_msg = (
		#		'Programme Outcome Set ({}) does not exist'.format(po_set_id))
		#	errors.add('path', 'po_set_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(
			po_set_id=po_set_id).first()
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

class AddProgrammeOutcome(Resource):
	def post(self,po_set_id):
		#errors = request.errors
		po_set = ProgrammeOutcomeSet.by_id(db.session, po_set_id)
		#if po_set is None:
		#	error_msg = (
		#    	'Programme Outcome Set ({}) does not exist'.format(po_set_id))
		#	errors.add('path', 'po_set_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		#if can_add_programme_outcome(dbsession, po_set) is False:
		#	error_msg = (
		#    	"Programme Outcome Set ({}) in use. Can't add programme outcome")
		#	errors.add('path', 'po_set_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return
		data={}
		data = request.json
		number = data['number']
		record = db.session.query(ProgrammeOutcome.id).filter_by(
			po_set_id=po_set_id, number=number).first()
		#if record is not None:
		#	error_msg = 'Programme Outcome with number ({}) already exists'
		#	errors.add('body', 'number', error_msg.format(number))
		#	errors.status = HTTPBadRequest.code
		#	return

		record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(
			po_set_id=po_set_id).first()
		if record[0] is not None:
			max_po = record[0]
		else:
			max_po = 0

		#if number != max_po + 1:
		#	err_msg = 'Programme Outcome numbers must be consecutive'
		#	errors.add('body', 'number', err_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		po = ProgrammeOutcome()
		po.number = number
		po.title = data['title']
		po.description = data['description']
		po.po_set_id = po_set_id
		db.session.add(po)
		db.session.commit()
#curl example -> curl -d '{"number":"3","title":"addnew","description":"testing"}' -H "Content-Type: application/json"  http://localhost:5000//ui/programme_outcome_manager/1/programme_outcomes -X POST


class EditProgrammeOutcome(Resource):
	def put(self,po_id):
		#errors = request.errors
		po = ProgrammeOutcome.by_id(db.session, po_id)
		#if po is None:
		#	error_msg = 'Programme Outcome ({}) does not exist'.format(po_id)
		#	errors.add('path', 'po_set_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return
		data={}
		data = request.json
		po.title = data['title']
		po.description = data['description']
		db.session.commit()
#curl example -> curl -d '{"title":"add","description":"testing complete"}' -H "Content-Type: application/json"  http://localhost:5000/ui/programme_outcome_manager/programme_outcome/1 -X PUT

class DeleteProgrammeOutcome(Resource):
	def delete(self,po_id):
		#errors = request.errors
		po = ProgrammeOutcome.by_id(db.session, po_id)
		#if po is None:
		#	error_msg = 'Programme Outcome ({}) does not exist'.format(po_id)
		#	errors.add('path', 'po_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		record = db.session.query(func.max(ProgrammeOutcome.number)).filter_by(
			po_set_id=po.po_set_id).first()
		max_po = record[0]
		#if po.number != max_po:
		#	error_msg = 'Only last Programme Outcome can be deleted'
		#	errors.add('path', 'po_id', error_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

		#if can_delete_programme_outcome(db.session, po) is False:
		#	err_msg = "Programme Outcome ({}) in use".format(po_id)
		#	errors.add("path", "id", err_msg)
		#	errors.status = HTTPBadRequest.code
		#	return

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
	app.run(debug=True)
