# from flask import Flask, request, abort
# import psycopg2
# from flask_sqlalchemy import SQLAlchemy
# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xdoqjfnpulfpjo:768aecc4b83a256b20adf6c1bf5d58f61565b2bcd165ef04f2f544f848d92980@ec2-54-163-229-212.compute-1.amazonaws.com:5432/daq90bi30jt6k4'

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

# class UserData(db.Model):
#     __tablename__ = 'UserData'

#     Pk = db.Column(db.Integer, primary_key=True)
#     Id = db.Column(db.String(100))
#     Text = db.Column(db.String(10))
    
#     def __init__(self
#                  , Id
#                  , Text
#                  ):
#         self.Id = Id
#         self.Text = Text


# if __name__ == '__main__':
#     manager.run()


