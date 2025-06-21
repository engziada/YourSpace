from app import app,db,models
import os


        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        models.create_default_admin()
        # Verbose: print default admin credentials
        print("\n=== Default Admin Credentials ===")
        print("Username:", 'admin2')
        print("Password:", 'admin2')
        print("Email:", 'fake2@email.com')
        print("\n=== Database Engine Info ===")
        print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
        engine = db.engine  # updated for Flask-SQLAlchemy 3.x
        print("DB Engine:", engine.name)
        print("DB Driver:", engine.driver)
        print("DB URL:", str(engine.url))
        print("==============================\n")
    app.run(debug=True)


'''
 flask db init   
 flask db migrate -m "..."
 flask db upgrade                             
'''
