from django.contrib import messages

# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from exercisesApp.utils.db_connection import get_db_connection


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        connection = get_db_connection('login_view')
        print(f'connection-------------{connection}')
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM Users WHERE fname = %s", [username])
            user = cursor.fetchone()

        if user and check_password(password, user[1]):  # Check hashed password
            request.session['user_id'] = user[0]  # Store user session
            return redirect('exercisesAppName:exercises_list')
        else:
            messages.error(request, 'Invalid username or password.')
            connection.close()

    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        password = make_password(request.POST.get('password'))  # Hash password
        dateOfBirth = request.POST.get('dateOfBirth')
        gender = request.POST.get('gender')
        level = request.POST.get('level')
        weight = request.POST.get('weight')
        height = request.POST.get('height')

        # Store fname and lname in the session
        request.session['fname'] = fname
        request.session['lname'] = lname

        connection = get_db_connection('signup_view')
        print(f'connection-------------{connection}')

        if not connection:
            messages.error(request, "Database connection failed!")
            return redirect("accounts:signup")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Users WHERE fname=%s AND lname=%s", (fname, lname))
                user = cursor.fetchone()

                if user:
                    messages.error(request, "User already exists!")
                else:
                    cursor.execute(
                        "INSERT INTO Users (fname, lname, password, dateOfBirth, gender, level, weight, height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (fname, lname, password, dateOfBirth, gender, level, weight, height),
                    )
                    connection.commit()
                    user_id = get_user_id_by_name(fname, lname)
                    generate_recommendations(user_id, level)
                    messages.success(request, "Account created successfully. You can log in now.")
                    return redirect("accounts:login")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        finally:
            connection.close()

    return render(request, "accounts/signup.html")


def home_view(request):
    if 'user_id' not in request.session:
        return redirect('accounts:login')

    return render(request, 'exercisesAppName:exercises_list')


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def get_user_id_by_name(fname, lname):
    connection = get_db_connection('get_user_id_by_name')
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM Users WHERE fname = %s AND lname = %s
            """, (fname, lname))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the user ID
            else:
                return None
    except Exception as e:
        print(f"Error retrieving user ID: {e}")
        return None


def generate_recommendations(user_id, user_level):
    connection = get_db_connection('generate_recommendations')
    try:
        with connection.cursor() as cursor:
            # Fetch exercises based on user level
            cursor.execute("""
                SELECT id, equipmentId FROM Exercise WHERE level = %s
            """, (user_level,))
            exercises = cursor.fetchall()

            recommendations = []
            for exercise_id, equipment_id in exercises:
                recommendations.append((user_id, equipment_id, user_level, 3, 12, exercise_id))

            # SQL INSERT statement with placeholders
            sql = """
            INSERT INTO Recommendations (userId, equipmentId, level, sets, reps, exerciseId)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Execute the INSERT statement for each recommendation
            cursor.executemany(sql, recommendations)
            connection.commit()

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        connection.rollback()
