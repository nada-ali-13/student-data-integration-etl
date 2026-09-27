from http.server import BaseHTTPRequestHandler, HTTPServer
import json


students = [
    {
        "student_id": 1001,
        "gpa": 3.45,
        "attendance": 92,
        "status": "Active"
    },
    {
        "student_id": 1002,
        "gpa": 3.80,
        "attendance": 95,
        "status": "Active"
    },
    {
        "student_id": 1003,
        "gpa": 2.90,
        "attendance": 78,
        "status": "Active"
    },
    {
        "student_id": 1004,
        "gpa": 3.60,
        "attendance": 88,
        "status": "Active"
    },
    {
        "student_id": 1005,
        "gpa": 3.20,
        "attendance": 72,
        "status": "Active"
    },
    {
        "student_id": 1006,
        "gpa": 3.90,
        "attendance": 97,
        "status": "Active"
    },
    {
        "student_id": 1007,
        "gpa": 4.50,
        "attendance": 80,
        "status": "Active"
    },
    {
        "student_id": 1008,
        "gpa": 2.70,
        "attendance": 83,
        "status": "Active"
    },
    {
        "student_id": 1009,
        "gpa": None,
        "attendance": 76,
        "status": "Active"
    },
    {
        "student_id": 1010,
        "gpa": 3.10,
        "attendance": 105,
        "status": "Active"
    }
]


class StudentAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/students":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = json.dumps(students)
            self.wfile.write(response.encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


server = HTTPServer(("127.0.0.1", 8000), StudentAPIHandler)

print("Mock API running at http://127.0.0.1:8000/students")
print("Press Ctrl+C to stop.")

server.serve_forever()