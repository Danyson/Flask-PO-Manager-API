from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from meta import metadata
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'insert db uri'

#"postgresql://postgres:postgres@localhost:5432/cars_api"

db = SQLAlchemy(app, metadata=metadata)




class ProgrammeOutcomeSet(db.Model):
    __tablename__ = "programme_outcome_sets"

    id = db.Column(db.Integer,primary_key=True)
    # a descriptive name to identify a PO set
    name = db.Column(db.String(512), nullable=False)

    @classmethod
    def by_id(cls, dbsession, id):
        return dbsession.query(ProgrammeOutcomeSet).filter_by(id=id).first()

    @classmethod
    def by_name(cls,dbsession,name):
        return dbsession.query(ProgrammeOutcomeSet).filter_by(name=name).first()


class ProgrammeOutcome(db.Model):
    __tablename__ = "programme_outcomes"
    __table_args__ = (db.UniqueConstraint('number', 'po_set_id'),)

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128))
    description = db.Column(db.String(4096), nullable=False)

    po_set_id = db.Column(db.Integer, db.ForeignKey("programme_outcome_sets.id"), nullable=False)
    po_set = db.relationship("ProgrammeOutcomeSet",backref=db.backref("programme_outcomes", lazy="dynamic"))

    @classmethod
    def by_id(cls, dbsession, id):
        return dbsession.query(ProgrammeOutcome).filter_by(id=id).first()

    def __lt__(self, other):
        return self.number < other.number
