

from flask import Flask, request, jsonify
from app.database import SessionLocal, Base, engine
from app.models import User, Worker, Property, TimeRecord
from datetime import datetime, date, timedelta
from functools import wraps
from jose import JWTError, jwt
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)
app = Flask(__name__)
SECRET_KEY = "dc-landscaping-secret-key-change-in-production"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

def verify_password(p, h):
    return pwd_context.verify(p, h)

def create_access_token(data):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=7)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    payload = decode_token(auth.split(' ')[1])
    if not payload:
        return None
    db = SessionLocal()
    user = db.query(User).filter(User.username == payload.get('sub')).first()
    db.close()
    return user

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        if not get_current_user():
            return jsonify({"detail": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def root():
    return jsonify({"status": "ok"})

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.json
    db = SessionLocal()
    user = db.query(User).filter(User.username == data['username']).first()
    db.close()
    if not user or not verify_password(data['password'], user.hashed_password):
        return jsonify({"detail": "Invalid credentials"}), 401
    return jsonify({"access_token": create_access_token({"sub": user.username, "role": user.role.value}), "token_type": "bearer"})

@app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
@login_required
def get_me():
    user = get_current_user()
    return jsonify({"id": user.id, "username": user.username, "email": user.email, "role": user.role.value})

@app.route('/api/workers', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def workers():
    db = SessionLocal()
    if request.method == 'GET':
        result = [{"id": w.id, "name": w.name, "phone": w.phone, "hourly_rate": str(w.hourly_rate), "is_active": w.is_active} for w in db.query(Worker).all()]
    else:
        data = request.json
        w = Worker(name=data['name'], phone=data.get('phone'), hourly_rate=data.get('hourly_rate', 20), is_active=True)
        db.add(w)
        db.commit()
        db.refresh(w)
        result = {"id": w.id, "name": w.name}
    db.close()
    return jsonify(result)

@app.route('/api/workers/<int:wid>', methods=['PUT', 'DELETE', 'OPTIONS'])
@login_required
def worker_detail(wid):
    db = SessionLocal()
    w = db.query(Worker).filter(Worker.id == wid).first()
    if request.method == 'PUT':
        for k, v in request.json.items():
            setattr(w, k, v)
        db.commit()
        result = {"id": w.id, "name": w.name}
    else:
        if w:
            db.delete(w)
            db.commit()
        result = {"ok": True}
    db.close()
    return jsonify(result)

@app.route('/api/properties', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def properties():
    db = SessionLocal()
    if request.method == 'GET':
        result = [{"id": p.id, "name": p.name, "address": p.address, "is_spring_cleanup": p.is_spring_cleanup, "is_fall_cleanup": p.is_fall_cleanup, "is_active": p.is_active} for p in db.query(Property).all()]
    else:
        data = request.json
        p = Property(name=data['name'], address=data.get('address'), is_spring_cleanup=data.get('is_spring_cleanup', False), is_fall_cleanup=data.get('is_fall_cleanup', False), is_active=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        result = {"id": p.id, "name": p.name}
    db.close()
    return jsonify(result)

@app.route('/api/properties/<int:pid>', methods=['PUT', 'DELETE', 'OPTIONS'])
@login_required
def property_detail(pid):
    db = SessionLocal()
    p = db.query(Property).filter(Property.id == pid).first()
    if request.method == 'PUT':
        for k, v in request.json.items():
            setattr(p, k, v)
        db.commit()
        result = {"id": p.id}
    else:
        if p:
            db.delete(p)
            db.commit()
        result = {"ok": True}
    db.close()
    return jsonify(result)

@app.route('/api/time-records/today', methods=['GET', 'OPTIONS'])
@login_required
def today_records():
    db = SessionLocal()
    records = db.query(TimeRecord).filter(TimeRecord.date == date.today()).all()
    result = [{"id": r.id, "property_id": r.property_id, "worker_id": r.worker_id, "start_time": r.start_time.isoformat() if r.start_time else None, "property": {"id": r.property.id, "name": r.property.name} if r.property else None, "worker": {"id": r.worker.id, "name": r.worker.name} if r.worker else None} for r in records]
    db.close()
    return jsonify(result)

@app.route('/api/time-records/start', methods=['POST', 'OPTIONS'])
@login_required
def start_timer():
    data = request.json
    db = SessionLocal()
    w = db.query(Worker).filter(Worker.id == data['worker_id']).first()
    r = TimeRecord(property_id=data['property_id'], worker_id=data['worker_id'], date=date.today(), start_time=datetime.now(), hourly_rate=w.hourly_rate if w else 20)
    db.add(r)
    db.commit()
    db.refresh(r)
    result = {"id": r.id, "start_time": r.start_time.isoformat()}
    db.close()
    return jsonify(result)

@app.route('/api/time-records/stop', methods=['POST', 'OPTIONS'])
@login_required
def stop_timer():
    data = request.json
    db = SessionLocal()
    r = db.query(TimeRecord).filter(TimeRecord.id == data['record_id']).first()
    if r:
        r.end_time = datetime.now()
        delta = r.end_time - r.start_time
        r.hours_worked = round(delta.total_seconds() / 3600, 2)
        r.total_cost = float(r.hours_worked) * float(r.hourly_rate) if r.hourly_rate else 0
        db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route('/api/time-records', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def time_records():
    db = SessionLocal()
    if request.method == 'GET':
        result = [{"id": r.id, "property_id": r.property_id, "worker_id": r.worker_id, "date": r.date.isoformat() if r.date else None, "hours_worked": str(r.hours_worked) if r.hours_worked else None, "property": {"id": r.property.id, "name": r.property.name} if r.property else None, "worker": {"id": r.worker.id, "name": r.worker.name} if r.worker else None} for r in db.query(TimeRecord).all()]
    else:
        data = request.json
        wid = data.get('worker_id')
        w = db.query(Worker).filter(Worker.id == wid).first() if wid else None
        r = TimeRecord(property_id=data.get('property_id'), worker_id=wid, date=date.today(), hours_worked=data.get('hours_worked'), hourly_rate=w.hourly_rate if w else 20)
        if r.hours_worked and r.hourly_rate:
            r.total_cost = float(r.hours_worked) * float(r.hourly_rate)
        db.add(r)
        db.commit()
        result = {"id": r.id}
    db.close()
    return jsonify(result)

@app.route('/api/time-records/<int:rid>', methods=['DELETE', 'OPTIONS'])
@login_required
def delete_record(rid):
    db = SessionLocal()
    r = db.query(TimeRecord).filter(TimeRecord.id == rid).first()
    if r:
        db.delete(r)
        db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route('/api/reports/dashboard', methods=['GET', 'OPTIONS'])
@login_required
def dashboard():
    db = SessionLocal()
    result = {"total_workers": db.query(Worker).count(), "total_properties": db.query(Property).count(), "total_records": db.query(TimeRecord).count()}
    db.close()
    return jsonify(result)
'''
with open('flask_app.py', 'w') as f:
    f.write(code)
print("Done!")
PYEOF
