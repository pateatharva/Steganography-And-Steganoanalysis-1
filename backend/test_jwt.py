from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dev-secret-fixed'
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

print("Creating token...")
with app.app_context():
    token = create_access_token(identity=str(1), expires_delta=timedelta(days=1))
    print(f"Token: {token[:50]}...")
    
print("\nNow testing if we can decode it...")
import jwt as pyjwt
try:
    decoded = pyjwt.decode(token, 'dev-secret-fixed', algorithms=['HS256'])
    print(f"Decoded successfully: {decoded}")
except Exception as e:
    print(f"Failed to decode: {e}")
