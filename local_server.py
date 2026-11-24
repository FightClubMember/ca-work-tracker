import os
import json
import psycopg
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = 8080
DIRECTORY = r"C:\Users\Himanshu Kumar\.gemini\antigravity\scratch\ymc_work_tracker"
CONN_STR = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_kSJ9La4cECpq@ep-little-hat-bkmnlplt-pooler.c-2.ap-southeast-2.aws.neon.tech/neondb?sslmode=require")

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/db':
            query = urllib.parse.parse_qs(parsed.query)
            try:
                with psycopg.connect(CONN_STR) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT id, username, password_hash, name, role, email, client_id FROM users;")
                        users = [{"id": r[0], "username": r[1], "password_hash": r[2], "name": r[3], "role": r[4], "email": r[5], "client_id": r[6]} for r in cur.fetchall()]

                        cur.execute("SELECT id, name, pan, gstin, type, phone, email, billing_rate FROM clients;")
                        clients = [{"id": r[0], "name": r[1], "pan": r[2], "gstin": r[3], "type": r[4], "phone": r[5], "email": r[6], "billing_rate": float(r[7] or 1500)} for r in cur.fetchall()]

                        cur.execute("SELECT id, client_id, title, type, emp_id, TO_CHAR(due_date, 'YYYY-MM-DD'), priority, status, est_hours, billable, TO_CHAR(completed_on, 'YYYY-MM-DD'), completed_by FROM tasks;")
                        tasks = [{"id": r[0], "client": r[1], "title": r[2], "type": r[3], "emp": r[4], "due": r[5], "priority": r[6], "status": r[7], "estHours": float(r[8] or 0), "billable": r[9], "completedOn": r[10], "completedBy": r[11]} for r in cur.fetchall()]

                        cur.execute("SELECT id, TO_CHAR(date, 'YYYY-MM-DD'), client_id, emp_id, work, hours, billable FROM logs;")
                        logs = [{"id": r[0], "date": r[1], "client": r[2], "emp": r[3], "work": r[4], "hours": float(r[5] or 0), "billable": r[6]} for r in cur.fetchall()]

                        cur.execute("SELECT id, title, category, period, TO_CHAR(due_date, 'YYYY-MM-DD'), penalty FROM compliances;")
                        compliances = [{"id": r[0], "title": r[1], "cat": r[2], "period": r[3], "due": r[4], "penalty": r[5]} for r in cur.fetchall()]

                        payload = {
                            "users": users,
                            "clients": clients,
                            "tasks": tasks,
                            "logs": logs,
                            "compliances": compliances
                        }

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(payload).encode('utf-8'))
                        return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/db':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            req = json.loads(body.decode('utf-8'))
            action = req.get('action')
            table = req.get('table')
            data = req.get('data')
            item_id = req.get('id')

            try:
                with psycopg.connect(CONN_STR) as conn:
                    with conn.cursor() as cur:
                        if action == 'insert':
                            if table == 'tasks':
                                cur.execute("""
                                    INSERT INTO tasks (id, client_id, title, type, emp_id, due_date, priority, status, est_hours, billable)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE SET
                                    client_id = EXCLUDED.client_id,
                                    title = EXCLUDED.title,
                                    type = EXCLUDED.type,
                                    emp_id = EXCLUDED.emp_id,
                                    due_date = EXCLUDED.due_date,
                                    priority = EXCLUDED.priority,
                                    status = EXCLUDED.status,
                                    est_hours = EXCLUDED.est_hours,
                                    billable = EXCLUDED.billable;
                                """, (data['id'], data['client'], data['title'], data['type'], data['emp'], data.get('due') or None, data.get('priority', 'Medium'), data.get('status', 'Pending'), data.get('estHours', 0), data.get('billable', True)))
                            elif table == 'logs':
                                cur.execute("""
                                    INSERT INTO logs (id, date, client_id, emp_id, work, hours, billable)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE SET
                                    date = EXCLUDED.date,
                                    client_id = EXCLUDED.client_id,
                                    emp_id = EXCLUDED.emp_id,
                                    work = EXCLUDED.work,
                                    hours = EXCLUDED.hours,
                                    billable = EXCLUDED.billable;
                                """, (data['id'], data['date'], data['client'], data['emp'], data['work'], data.get('hours', 1), data.get('billable', True)))
                            elif table == 'clients':
                                cur.execute("""
                                    INSERT INTO clients (id, name, pan, gstin, type, phone, email, billing_rate)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE SET
                                    name = EXCLUDED.name,
                                    pan = EXCLUDED.pan,
                                    gstin = EXCLUDED.gstin,
                                    type = EXCLUDED.type,
                                    phone = EXCLUDED.phone,
                                    email = EXCLUDED.email,
                                    billing_rate = EXCLUDED.billing_rate;
                                """, (data['id'], data['name'], data.get('pan', ''), data.get('gstin', ''), data.get('type', 'Company'), data.get('phone', ''), data.get('email', ''), data.get('billingRate', 1500)))
                            elif table == 'users':
                                cur.execute("""
                                    INSERT INTO users (id, username, password_hash, name, role, email, client_id)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE SET
                                    password_hash = EXCLUDED.password_hash,
                                    name = EXCLUDED.name,
                                    role = EXCLUDED.role,
                                    email = EXCLUDED.email,
                                    client_id = EXCLUDED.client_id;
                                """, (data['id'], data['username'], data.get('password_hash'), data['name'], data['role'], data.get('email', ''), data.get('client_id')))
                            conn.commit()

                        elif action == 'delete':
                            if table in ['tasks', 'logs', 'clients', 'users', 'compliances']:
                                cur.execute(f"DELETE FROM {table} WHERE id = %s;", (item_id,))
                                conn.commit()

                        elif action == 'update_task_done':
                            cur.execute("""
                                UPDATE tasks SET status = 'Completed', completed_on = %s, completed_by = %s WHERE id = %s;
                            """, (data['completedOn'], data['completedBy'], item_id))
                            conn.commit()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"success":true}')
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

if __name__ == '__main__':
    print(f"Starting server on http://localhost:{PORT}")
    server = HTTPServer(('127.0.0.1', PORT), CustomHandler)
    server.serve_forever()
