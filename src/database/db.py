from src.database.config import supabase
import bcrypt


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Checks for unique username, returns True when username is already taken
    response = supabase.table("teachers").select(
        "username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, password, name):
    data = {"username": username,
            "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select(
        "*").eq("username", username).execute()

    if response.data:
        teacher = response.data[0]

        if check_pass(password, teacher['password']):
            return teacher
        return None


def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data


def create_student(new_name, face_embedding=None, voice_embedding=None):
    
    data={
      "name": new_name,
      "face_embedding": face_embedding,
      "voice_embedding": voice_embedding
    }

    response=supabase.table("students").insert(data).execute()

    return response.data
    
def create_subject(sub_id, sub_name, sub_section, teacher_id):
  data={
    "subject_code": sub_id,
    "name":sub_name,
    "section":sub_section,
    "teacher_id":teacher_id
  }

  response=supabase.table("subjects").insert(data).execute()

  return response.data

def get_teacher_subjects(teacher_id):

  #supabase feature which allows postgres to automatically join the table based on foreign keys
  #and extracts number of records from subject_students table and the timestamp column from the attendance logs table
  #of a particular teacher

  response=supabase.table("subjects").select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
  
  subjects=response.data
  #subject structure
  # [
  #     {
  #         "subject_id": 10,
  #         "subject_code": "CS101",
  #         "name": "Machine Learning",
  #         "section": "A",
  #         "teacher_id": 1,
  #         "subject_students": [
  #             {"count": 40}            # <-- Supabase nested count
  #         ],
  #         "attendance_logs": [         # <-- Supabase nested list of logs
  #             {"timestamp": "2026-09-10T10:00:00Z"},
  #             {"timestamp": "2026-09-10T10:00:00Z"},  # student 2 in same class
  #             {"timestamp": "2026-09-12T10:00:00Z"}  # next class
  #         ]
  #     },
  #     {
  #         second subject handled by the teacher if any
  #     }
  #     ... so on
  # ]


  for sub in subjects:
    sub['total_students']=sub.get("subject_students",[{}])[0].get('count',0) if sub.get('subject_students') else 0
    attendance=sub.get('attendance_logs',[])

    #attendance_logs structure 
    # [
    #   {"timestamp": "2026-09-10T10:00:00Z"},
    #   {"timestamp": "2026-09-10T10:00:00Z"},  # student 2 in same class
    #   {"timestamp": "2026-09-12T10:00:00Z"}  # next class
    # ]
    
    unique_sessions=len(set(log['timestamp'] for log in attendance))
    
    # without set : (log['timestamp'] for log in attendance)
    # Result: ["10:00 AM", "10:00 AM", "11:00 AM"]
    # with set    : set(log['timestamp'] for log in attendance)
    # Result: {"10:00 AM", "11:00 AM"}
    # len() counts the number of unique sessions

    sub['total_classes']=unique_sessions #total classes taken by the teacher

    sub.pop('subject_students', None) #removes the subject_students key from the subject dictionary
    # since we stored the count (number of students) key inside it as a new separate key as total_students
    
    sub.pop('attendance_logs', None) #removes the attendance_logs key from the subject dictionary
    # since we stored the count of unique sessions inside it as a new separate key as total_classes
    
    # Raw DB Result:


    # {
    #   "subject_id": 10,
    #   "subject_code": "CS101",
    #   "name": "Machine Learning",
    #   "section": "A",
    #   "teacher_id": 1,
    #   "subject_students": [{"count": 40}],
    #   "attendance_logs": [{"timestamp": "10:00"}, {"timestamp": "10:00"}]
    # }
    # │
    # ▼(Python transforms it)
    # Clean UI-Ready Result:
    # {
    #   "subject_id": 10,
    #   "subject_code": "CS101",
    #   "name": "Machine Learning",
    #   "section": "A",
    #   "teacher_id": 1,
    #   "total_students": 40,
    #   "total_classes": 1
    # }

    # if multiple subjects, list of subjects looks like this: 

    #[
    #   {
    #     "subject_id": 10,
    #     "subject_code": "CS101",
    #     "name": "Machine Learning",
    #     "section": "A",
    #     "teacher_id": 1,
    #     "total_students": 40,
    #     "total_classes": 1
    #   },
    #   {
    #     "subject_id": 11,
    #     "subject_code": "CS102",
    #     "name": "Computer Networks",
    #     "section": "B",
    #     "teacher_id": 1,
    #     "total_students": 35,
    #     "total_classes": 3
    #   }
    #   ... so on
    #]


  return subjects  

def enroll_student_to_subject(student_id, subject_id):

  data={
    "subject_id":subject_id,
    "student_id":student_id
  }

  response=supabase.table("subject_students").insert(data).execute()

  return response.data


def unenroll_student_to_subject(student_id, subject_id):

  response = supabase.table("subject_students").delete().eq("student_id",student_id).eq("subject_id",subject_id).execute()
  

  return response.data


def get_student_subjects(student_id):

  response=supabase.table("subject_students").select("*, subjects(*)").eq('student_id', student_id).execute() #joins with subject to get names and other info of the subjects

  return response.data

  # Output structure
  # [
  #     {
  #         "id": 1,                      # ID of the enrollment record
  #         "student_id": 5,              # The student's ID
  #         "subject_id": 10,             # Foreign key to subjects
  #         "created_at": "2026-09-14T...",
  #         "subjects": {                 # <-- Nested dict from the joined 'subjects' table
  #             "subject_id": 10,
  #             "subject_code": "CS101",
  #             "name": "Machine Learning",
  #             "section": "A",
  #             "teacher_id": 1
  #         }
  #     },
  #     {
  #         "id": 2,
  #         "student_id": 5,
  #         "subject_id": 11,
  #         "created_at": "2026-09-15T...",
  #         "subjects": {
  #             "subject_id": 11,
  #             "subject_code": "CS102",
  #             "name": "Computer Networks",
  #             "section": "B",
  #             "teacher_id": 2
  #         }
  #     }
  # ]


def get_student_attendance(student_id):
  
  response=supabase.table("attendance_logs").select("*, subjects(*)").eq('student_id', student_id).execute() #joins with subject to get names and other info of the subjects

  return response.data

  # Output structure

  # [
  #     {
  #         "id": 101,                     # Attendance log ID
  #         "student_id": 5,
  #         "subject_id": 10,
  #         "timestamp": "2026-09-10T10:00:00Z",  # Date/Time attendance was marked
  #         "is_present": 0/1,
  #         "subjects": {                  # <-- Nested dict from the joined 'subjects' table
  #             "subject_id": 10,
  #             "subject_code": "CS101",
  #             "name": "Machine Learning",
  #             "section": "A",
  #             "teacher_id": 1
  #         }
  #     },
  #     {
  #         "id": 102,
  #         "student_id": 5,
  #         "subject_id": 10,
  #         "timestamp": "2026-09-12T10:00:00Z",  # Another class of the same subject
  #         "is_present": 0/1,
  #         "subjects": {
  #             "subject_id": 10,
  #             "subject_code": "CS101",
  #             "name": "Machine Learning",
  #             "section": "A",
  #             "teacher_id": 1
  #         }
  #     }
  # ]


def create_attendance(attendance_logs):

  response=supabase.table("attendance_logs").insert(attendance_logs).execute()

  return response.data


def get_attendance_for_teacher(teacher_id):

  response=supabase.table("attendance_logs").select("*, subjects!inner(*)").eq("subjects.teacher_id",teacher_id).execute()

  return response.data
  