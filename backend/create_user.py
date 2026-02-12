from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='Zelseeh').first()
    
    if user:
        print(f"Użytkownik {user.username} już istnieje!")
    else:
        new_user = User(
            username='Zelseeh',
            email='zelseeh@filmhive.com',
            name='Zelseeh'
        )
        new_user.set_password('ZAQ!2wsx')
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"Utworzono użytkownika: {new_user.username}")
        print(f"Email: {new_user.email}")
