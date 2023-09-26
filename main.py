from app import app,db,models


        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        models.create_default_admin()
    app.run(debug=True)


'''
 flask db init   
 flask db migrate -m "..."
 flask db upgrade                             
'''
