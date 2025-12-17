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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
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
    token = auth.split(' ')[1]
    payload = decode_token(token)
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
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def root():
    return jsonify({"status": "ok", "app": "DC Landscaping"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

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
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return jsonify({"access_token": token, "token_type": "bearer"})

@app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
@login_required
def get_me():
    user = get_current_user()
    return jsonify({"id": user.id, "username": user.username, "email": user.email, "role": user.role.value})

@app.route('/api/workers', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def workers():
    if request.method == 'GET':
        db = SessionLocal()
        workers = db.query(Worker).all()
        result = [{"id": w.id, "name": w.name, "phone": w.phone, "hourly_rate": str(w.hourly_rate), "is_active": w.is_active} for w in workers]
        db.close()
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        db = SessionLocal()
        worker = Worker(name=data['name'], phone=data.get('phone'), hourly_rate=data.get('hourly_rate', 20), is_active=data.get('is_active', True))
        db.add(worker)
        db.commit()
        db.refresh(worker)
        result = {"id": worker.id, "name": worker.name, "phone": worker.phone, "hourly_rate": str(worker.hourly_rate), "is_active": worker.is_active}
        db.close()
        return jsonify(result)

@app.route('/api/workers/<int:worker_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@login_required
def worker_detail(worker_id):
    db = SessionLocal()
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if request.method == 'PUT':
        data = request.json
        if not worker:
            db.close()
            return jsonify({"detail": "Not found"}), 404
        for key, value in data.items():
            setattr(worker, key, value)
        db.commit()
        result = {"id": worker.id, "name": worker.name, "phone": worker.phone, "hourly_rate": str(worker.hourly_rate), "is_active": worker.is_active}
        db.close()
        return jsonify(result)
    elif request.method == 'DELETE':
        if worker:
            db.delete(worker)
            db.commit()
        db.close()
        return jsonify({"ok": True})

@app.route('/api/properties', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def properties():
    if request.method == 'GET':
        db = SessionLocal()
        props = db.query(Property).all()
        result = [{"id": p.id, "name": p.name, "address": p.address, "is_spring_cleanup": p.is_spring_cleanup, "is_fall_cleanup": p.is_fall_cleanup, "is_active": p.is_active} for p in props]
        db.close()
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        db = SessionLocal()
        prop = Property(name=data['name'], address=data.get('address'), is_spring_cleanup=data.get('is_spring_cleanup', False), is_fall_cleanup=data.get('is_fall_cleanup', False), is_active=data.get('is_active', True))
        db.add(prop)
        db.commit()
        db.refresh(prop)
        result = {"id": prop.id, "name": prop.name, "address": prop.address, "is_spring_cleanup": prop.is_spring_cleanup, "is_fall_cleanup": prop.is_fall_cleanup, "is_active": prop.is_active}
        db.close()
        return jsonify(result)

@app.route('/api/properties/<int:property_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@login_required
def property_detail(property_id):
    db = SessionLocal()
    prop = db.query(Property).filter(Property.id == property_id).first()
    if request.method == 'PUT':
        data = request.json
        if not prop:
            db.close()
            return jsonify({"detail": "Not found"}), 404
        for key, value in data.items():
            setattr(prop, key, value)
        db.commit()
        result = {"id": prop.id, "name": prop.name, "address": prop.address, "is_spring_cleanup": prop.is_spring_cleanup, "is_fall_cleanup": prop.is_fall_cleanup, "is_active": prop.is_active}
        db.close()
        return jsonify(result)
    elif request.method == 'DELETE':
        if prop:
            db.delete(prop)
            db.commit()
        db.close()
        return jsonify({"ok": True})

@app.route('/api/time-records/today', methods=['GET', 'OPTIONS'])
@login_required
def get_today_records():
    db = SessionLocal()
    today = date.today()
    records = db.query(TimeRecord).filter(TimeRecord.date == today).all()
    result = []
    for r in records:
        result.append({
            "id": r.id, "property_id": r.property_id, "worker_id": r.worker_id,
            "date": r.date.isoformat() if r.date else None,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "end_time": r.end_time.isoformat() if r.end_time else None,
            "hours_worked": str(r.hours_worked) if r.hours_worked else None,
            "property": {"id": r.property.id, "name": r.property.name} if r.property else None,
            "worker": {"id": r.worker.id, "name": r.worker.name} if r.worker else None
        })
    db.close()
    return jsonify(result)

@app.route('/api/time-records/start', methods=['POST', 'OPTIONS'])
@login_required
def start_timer():
    data = request.json
    db = SessionLocal()
    worker = db.query(Worker).filter(Worker.id == data['worker_id']).first()
    record = TimeRecord(property_id=data['property_id'], worker_id=data['worker_id'], date=date.today(), start_time=datetime.now(), hourly_rate=worker.hourly_rate if worker else 20)
    db.add(record)
    db.commit()
    db.refresh(record)
    result = {"id": record.id, "property_id": record.property_id, "worker_id": record.worker_id, "date": record.date.isoformat(), "start_time": record.start_time.isoformat()}
    db.close()
    return jsonify(result)

@app.route('/api/time-records/stop', methods=['POST', 'OPTIONS'])
@login_required
def stop_timer():
    data = request.json
    db = SessionLocal()
    record = db.query(TimeRecord).filter(TimeRecord.id == data['record_id']).first()
    if not record:
        db.close()
        return jsonify({"detail": "Not found"}), 404
    record.end_time = datetime.now()
    if record.start_time:
        delta = record.end_time - record.start_time
        record.hours_worked = round(delta.total_seconds() / 3600, 2)
        if record.hourly_rate:
            record.total_cost = float(record.hours_worked) * float(record.hourly_rate)
    db.commit()
    result = {"id": record.id, "hours_worked": str(record.hours_worked)}
    db.close()
    return jsonify(result)

@app.route('/api/time-records', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def time_records():
    if request.method == 'GET':
        db = SessionLocal()
        records = db.query(TimeRecord).all()
        result = []
        for r in records:
            result.append({
                "id": r.id, "property_id": r.property_id, "worker_id": r.worker_id,
                "date": r.date.isoformat() if r.date else None,
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "end_time": r.end_time.isoformat() if r.end_time else None,
                "hours_worked": str(r.hours_worked) if r.hours_worked else None,
                "property": {"id": r.property.id, "name": r.property.name} if r.property else None,
                "worker": {"id": r.worker.id, "name": r.worker.name} if r.worker else None
            })
        db.close()
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        db = SessionLocal()
        worker_id = data.get('worker_id')
        worker = db.query(Worker).filter(Worker.id == worker_id).first() if worker_id else None
        record = TimeRecord(property_id=data.get('property_id'), worker_id=worker_id, date=date.today(), hours_worked=data.get('hours_worked'), hourly_rate=worker.hourly_rate if worker else 20, notes=data.get('notes'))
        if record.hours_worked and record.hourly_rate:
            record.total_cost = float(record.hours_worked) * float(record.hourly_rate)
        db.add(record)
        db.commit()
        db.refresh(record)
        result = {"id": record.id}
        db.close()
        return jsonify(result)

@app.route('/api/time-records/<int:record_id>', methods=['DELETE', 'OPTIONS'])
@login_required
def delete_time_record(record_id):
    db = SessionLocal()
    record = db.query(TimeRecord).filter(TimeRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route('/api/reports/dashboard', methods=['GET', 'OPTIONS'])
@login_required
def get_dashboard():
    db = SessionLocal()
    workers = db.query(Worker).filter(Worker.is_active == True).count()
    properties = db.query(Property).filter(Property.is_active == True).count()
    records = db.query(TimeRecord).count()
    db.close()
    return jsonify({"total_workers": workers, "total_properties": properties, "total_records": records})

if __name__ == '__main__':
    app.run(debug=True)
