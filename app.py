from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt

# usernames cannot be more than 15 chars
# clan cannot be more than 15 chars
# rank cannot be more than 15 chars
# status cannot be more than 15 chars

app = Flask(__name__)
heroku = Heroku(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://oxzqkchfssxhjf:a0048232bd43dc769cc40f25bff26e410ff43b4bbb67cb95db1ecb35b4da0c9e@ec2-54-243-239-199.compute-1.amazonaws.com:5432/d4bq1f7ed7pd84'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
bcrypt = Bcrypt()
db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(15), unique=True)
  password = db.Column(db.String(120))
  clan = db.Column(db.String(15))
  rank = db.Column(db.String(15))
  status = db.Column(db.String(250))

  def __init__(self, username, password, clan, rank, status):
    self.username = username
    self.password = password
    self.clan = clan
    self.rank = rank
    self.status = status

  def __repr__(self):
    return '<{}>'.format(self.username)
  
class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'password', 'clan', 'rank', 'status')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# CREATE
@app.route('/user', methods=['POST'])
def create_user():
  username = request.json['username']
  password = request.json['password']
  clan = request.json['clan']
  rank = request.json['rank']
  status = request.json['status']

  hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

  new_user = User(username, hashed_password, clan, rank, status)

  db.session.add(new_user)
  db.session.commit()

  return user_schema.jsonify(new_user)

# GET ALL
@app.route('/users', methods=['GET'])
def get_users():
  all_users = User.query.all()
  results = users_schema.dump(all_users)
  return jsonify(results)

# GET SPECIFIC
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
  user = User.query.get(id)
  return user_schema.jsonify(user)

# CHECK LOGIN CREDENTIALS
@app.route('/login', methods=['POST'])
def check_password():
  all_users = User.query.all()
  results = users_schema.dump(all_users)

  username = request.json['username']
  password = request.json['password']

  for result in results:
    if result["username"] == username:
      if bcrypt.check_password_hash(result["password"], password):
        return "SUCCESSFUL LOGIN"
    return "FAILED LOGIN ATTEMPT"

# UPDATE SPECIFIC
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
  user = User.query.get(id)

  username = request.json['username']
  password = request.json['password']
  clan = request.json['clan']
  rank = request.json['rank']
  status = request.json['status']

  user.username = username
  user.password = hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
  user.clan = clan
  user.rank = rank
  user.status = status

  db.session.commit()

  return user_schema.jsonify(user)

# DELETE
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
  user = User.query.get(id)
  db.session.delete(user)
  db.session.commit()
  return f"SUCCESSFULLY DELETED USER {user.username}"

if __name__ == "__main__":
  app.run(debug=True)
