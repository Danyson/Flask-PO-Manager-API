from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api,reqparse
from models.meta import metadata

from .utils import (
    programme_outcome_set_to_dict,
    can_delete_programme_outcome_set,
)

from models.programme import ProgrammeOutcomeSet





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////UECRUD.db'
db = SQLAlchemy(app, metadata=metadata)
api = Api(app)





class GetProgrammeOutcomeSets(Resource):
	def get(self):
		po_sets = db.session.query(ProgrammeOutcomeSet)
    		result = []
    		for po_set in po_sets:
        		di = programme_outcome_set_to_dict(po_set)
        		di['po_count'] = po_set.programme_outcomes.count()
        		di['can_delete'] = can_delete_programme_outcome_set(dbsession, po_set)
        		result.append(di)
    	return {
        	'type': 'programme_outcome_set_list',
        	'result': result,}

api.add_resource(programmeoutcomesets,'/ui/programme_outcome_manager/programme_outcome_sets')


if __name__ == '__main__':
	app.run(debug=True)
