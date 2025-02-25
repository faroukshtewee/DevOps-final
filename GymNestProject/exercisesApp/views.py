from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

# Create your views here.
# from .models import Exercises, DailyExercise
from django.shortcuts import render, redirect
from .utils.db_connection import get_db_connection
from accounts.views import get_user_id_by_name
from django.contrib.auth.decorators import login_required
from datetime import datetime
from datetime import date, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from datetime import date, datetime, timedelta


def get_users():
    conn = get_db_connection('get_users')
    print(f'conn-------------------------------------------------------------------{conn}')
    if conn:
        cursor = conn.cursor(dictionary=True)  # Returns results as dictionaries
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        conn.close()
        return users
    return []


def users_list(request):
    users = get_users()
    return JsonResponse(users, safe=False)


def get_recommendations_with_exercise_details(user_id):
    connection = get_db_connection('get_recommendations_with_exercise_details')

    if connection:
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor to return results as dictionaries

        # SQL query to join tables and fetch recommendations with exercise details
        query = """
       SELECT 
            Recommendations.id AS recommendation_id,
            Recommendations.userId,
            Recommendations.level AS recommendation_level,
            Recommendations.sets,
            Recommendations.reps,
            Exercise.id AS exercise_id,
            Exercise.name_of_exercise,
            Exercise.level AS exercise_level,
            Exercise.`Desc`,
            Exercise.`Type`,
            Exercise.linkForVideo,
            Exercise.linkForImage,
            Equipment.name AS equipment_name,
            Equipment.imageUrl AS equipment_image
        FROM 
            Recommendations
        JOIN 
            Exercise ON Recommendations.exerciseId = Exercise.id
        JOIN 
            Equipment ON Exercise.equipmentId = Equipment.id
        WHERE 
            Recommendations.userId = %s;

        """

        # Execute the query with the provided user_id
        cursor.execute(query, (user_id,))

        # Fetch all results
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
        return results


def exercises_list(request):
    # Retrieve fname and lname from the session
    fname = request.session.get('fname')
    lname = request.session.get('lname')
    user_id = get_user_id_by_name(fname, lname)
    print(f'user_id-----------------------------------------\n{user_id}')
    search_query = request.GET.get("q", "")  # Get search query from URL
    exercises = []

    if search_query:
        exercises = search_exercises(search_query)
        print(f'exercises-----------------------------------------\n{exercises}')
        if not exercises:  # Handle case where no exercises match the search query
            return HttpResponse("No exercises found for the given search query", status=404)

    else:
        exercises = get_recommendations_with_exercise_details(user_id)
        print(f'exercises-----------------------------------------\n{exercises}')
        if not exercises:  # Check if no exercises were returned
            return HttpResponse("No exercises found", status=404)

    return render(request, 'exercises/exercises_list.html', {'exercises': exercises, 'query': search_query})


def search_exercises(query):
    conn = get_db_connection('search_exercises')
    cursor = conn.cursor(dictionary=True)

    # First, try to find an exact match
    exact_sql = """
    SELECT DISTINCT name_of_exercise, `Desc`, `Type`, `level` AS exercise_level
    FROM Exercise 
    WHERE name_of_exercise = %s 
    OR `Desc` = %s 
    OR `Type` = %s 
    OR `level` = %s
    """
    cursor.execute(exact_sql, (query, query, query, query))
    exact_match = cursor.fetchall()

    if exact_match:  # Return exact match if found
        cursor.close()
        conn.close()
        return exact_match

    # If no exact match, perform a partial match search
    partial_sql = """
    SELECT DISTINCT name_of_exercise, `Desc`, `Type`, `level`AS exercise_level
    FROM Exercise 
    WHERE name_of_exercise LIKE %s 
    OR `Desc` LIKE %s 
    OR `Type` LIKE %s 
    OR `level` LIKE %s
    """
    like_query = f"%{query}%"
    cursor.execute(partial_sql, (like_query, like_query, like_query, like_query))
    partial_matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return partial_matches  # Return partial matches if found


def fetch_progress_tracking(user_id, start_date, end_date):
    connection = get_db_connection('fetch_progress_tracking')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PT.id, E.name_of_exercise, PT.dateCompleted, PT.setsCompleted,
                   PT.repsCompleted, PT.duration, PT.caloriesBurned
            FROM `ProgressTracking` PT  -- Use backticks
            JOIN `Exercise` E ON PT.exerciseId = E.id
            WHERE PT.userId = %s AND PT.dateCompleted BETWEEN %s AND %s
        """, [user_id, start_date, end_date])  # Ensure datetime is correctly formatted

        columns = [col[0] for col in cursor.description]
        # return [dict(zip(columns, row)) for row in cursor.fetchall()]
        results = []
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            # Convert dateCompleted to string in YYYY-MM-DD format
            if data['dateCompleted']:  # Handle potential None values
                data['dateCompleted'] = data['dateCompleted'].strftime('%Y-%m-%d')
            results.append(data)
        return results


# def progress_tracking_api(request):
#     fname = request.session.get('fname')
#     lname = request.session.get('lname')
#     user_id = get_user_id_by_name(fname, lname)
#     start_date_str = request.GET.get('start')
#     end_date_str = request.GET.get('end')
#
#     if not (start_date_str and end_date_str):
#         today = date.today()
#         start_date = today - timedelta(days=today.weekday())
#         end_date = start_date + timedelta(days=6)
#     else:
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#
#     try:
#         connection = get_db_connection('progress_tracking_api')
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT PT.id, PT.exerciseId, PT.dateCompleted, PT.setsCompleted,
#                        PT.repsCompleted, PT.duration, PT.caloriesBurned, E.name_of_exercise
#                 FROM ProgressTracking PT
#                 INNER JOIN Exercise E ON PT.exerciseId = E.id
#                 WHERE PT.userId = %s AND PT.dateCompleted BETWEEN %s AND %s
#             """
#             cursor.execute(sql, [user_id, start_date, end_date])
#             columns = [col[0] for col in cursor.description]
#             progress_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
#
#             events = []
#             for item in progress_data:
#                 events.append({
#                     'id': item['id'],
#                     'title': item['name_of_exercise'],
#                     'start': item['dateCompleted'].strftime('%Y-%m-%dT00:00:00'),
#                     'sets': item['setsCompleted'],
#                     'reps': item['repsCompleted'],
#                     'duration': str(item['duration'].total_seconds()) + "s",
#                     'calories': str(item['caloriesBurned']),
#                 })
#
#             return JsonResponse(events, safe=False)
#
#     except Exception as e:
#         print(f"Error in progress_tracking_api: {e}")
#         return JsonResponse({'error': str(e)}, status=500)  # Return error as JSON
#     finally:
#         if connection:
#             connection.close()  # Close connection in finally block
# def progress_tracking(request):
#     fname = request.session.get('fname')
#     lname = request.session.get('lname')
#     user_id = get_user_id_by_name(fname, lname)
#     start_date_str = request.GET.get('start')
#     end_date_str = request.GET.get('end')
#
#     if not (start_date_str and end_date_str):
#         today = date.today()
#         start_date = today - timedelta(days=today.weekday())
#         end_date = start_date + timedelta(days=6)
#     else:
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#
#     try:
#         connection = get_db_connection('progress_tracking_api')
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT PT.id, PT.exerciseId, PT.dateCompleted, PT.setsCompleted,
#                        PT.repsCompleted, PT.duration, PT.caloriesBurned, E.name_of_exercise
#                 FROM ProgressTracking PT
#                 INNER JOIN Exercise E ON PT.exerciseId = E.id
#                 WHERE PT.userId = %s AND PT.dateCompleted BETWEEN %s AND %s
#             """
#             cursor.execute(sql, [user_id, start_date, end_date])
#             progress_data = [
#                 {
#                     'id': row[0],
#                     'title': row[7],  # Exercise name
#                     'start': row[2].strftime('%Y-%m-%dT00:00:00'),
#                     'extendedProps': {
#                         'sets': row[3],
#                         'reps': row[4],
#                         'duration': f"{row[5]} min",
#                         'calories': f"{row[6]} kcal"
#                     }
#                 }
#                 for row in cursor.fetchall()
#             ]
#             return JsonResponse(progress_data, safe=False)
#
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def progress_tracking1(request):
#     fname = request.session.get('fname')
#     lname = request.session.get('lname')
#     user_id = get_user_id_by_name(fname, lname)
#     start_date_str = request.GET.get('start')
#     end_date_str = request.GET.get('end')
#     exercises = get_recommendations_with_exercise_details(user_id)
#     # Check if the request is an AJAX request (API call from FullCalendar)
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         if not (start_date_str and end_date_str):
#             today = date.today()
#             start_date = today - timedelta(days=today.weekday())
#             end_date = start_date + timedelta(days=6)
#         else:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#
#         try:
#             connection = get_db_connection('progress_tracking')
#             with connection.cursor() as cursor:
#                 sql = """
#                     SELECT PT.id, PT.exerciseId, PT.dateCompleted, PT.setsCompleted,
#                            PT.repsCompleted, PT.duration, PT.caloriesBurned, E.name_of_exercise
#                     FROM ProgressTracking PT
#                     INNER JOIN Exercise E ON PT.exerciseId = E.id
#                     WHERE PT.userId = %s AND PT.dateCompleted BETWEEN %s AND %s
#                 """
#                 cursor.execute(sql, [user_id, start_date, end_date])
#
#                 progress_data = [
#                     {
#                         'id': row[0],
#                         'title': row[7],  # Exercise name
#                         'start': row[2].strftime('%Y-%m-%dT00:00:00'),
#                         'extendedProps': {
#                             'sets': row[3],
#                             'reps': row[4],
#                             'duration': f"{row[5]} min",
#                             'calories': f"{row[6]} kcal"
#                         }
#                     }
#                     for row in cursor.fetchall()
#                 ]
#                 return JsonResponse(progress_data, safe=False)
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     # Otherwise, return the HTML page
#     return render(request, 'exercises/progress_tracking.html', {'exercises': exercises})


def progress_tracking(request):
    fname = request.session.get('fname')
    lname = request.session.get('lname')
    user_id = get_user_id_by_name(fname, lname)
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    # If this is a FullCalendar API request, return JSON
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str[:10], '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str[:10], '%Y-%m-%d').date()

            connection = get_db_connection('progress_tracking')
            with connection.cursor() as cursor:
                sql = """
                    SELECT PT.id, PT.exerciseId, PT.dateCompleted, PT.setsCompleted,
                           PT.repsCompleted, PT.duration, PT.caloriesBurned, E.name_of_exercise
                    FROM ProgressTracking PT
                    INNER JOIN Exercise E ON PT.exerciseId = E.id
                    WHERE PT.userId = %s AND PT.dateCompleted BETWEEN %s AND %s
                """
                cursor.execute(sql, [user_id, start_date, end_date])

                progress_data = [
                    {
                        'id': row[0],
                        'title': row[7],  # Exercise name
                        'start': row[2].strftime('%Y-%m-%dT00:00:00'),
                        'extendedProps': {
                            'sets': row[3],
                            'reps': row[4],
                            'duration': f"{row[5]} min",
                            'calories': f"{row[6]} kcal"
                        }
                    }
                    for row in cursor.fetchall()
                ]

                return JsonResponse(progress_data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # If it's a normal page request, return HTML
    exercises = get_recommendations_with_exercise_details(user_id)
    return render(request, 'exercises/progress_tracking.html', {'exercises': exercises})

# def progress_tracking_view(request):
#     fname = request.session.get('fname')
#     lname = request.session.get('lname')
#     user_id = get_user_id_by_name(fname, lname)
#     today = date.today()
#
#     # Get start and end dates of the current week (Monday to Sunday)
#     start_of_week = today - timedelta(days=today.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#     print("progress_tracking_view user_id:", user_id)  # Print the exercises data
#     progress_data = fetch_progress_tracking(user_id, start_of_week, end_of_week)
#     # exercises = fetch_exercises()
#
#     exercises = get_recommendations_with_exercise_details(user_id)
#     # Prepare data for the calendar (a dictionary where keys are dates and values are lists of exercises)
#     calendar_data = {}
#     for item in progress_data:
#         date_completed = item['dateCompleted']
#         if date_completed not in calendar_data:
#             calendar_data[date_completed] = []
#         calendar_data[date_completed].append(item)
#
#     return render(request, 'exercises/progress_tracking.html',
#                   {'progress_data': progress_data, 'exercises': exercises, 'calendar_data': calendar_data,
#                    'current_week_start': start_of_week, })
# def progress_tracking_view(request):
#     fname = request.session.get('fname')
#     lname = request.session.get('lname')
#     user_id = get_user_id_by_name(fname, lname)
#     today = date.today()
#
#     start_of_week = today - timedelta(days=today.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#
#     progress_data = fetch_progress_tracking(user_id, start_of_week, end_of_week)
#     exercises = get_recommendations_with_exercise_details(user_id)
#
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check for AJAX request
#         events = [
#             {
#                 "id": item["id"],
#                 "title": f"{item['name_of_exercise']} ({item['setsCompleted']} sets)",
#                 "start": item["dateCompleted"].strftime('%Y-%m-%dT00:00:00'),
#                 "extendedProps": {
#                     "reps": item["repsCompleted"],
#                     "duration": f"{item['duration']} min",
#                     "calories": f"{item['caloriesBurned']} kcal"
#                 }
#             }
#             for item in progress_data
#         ]
#         return JsonResponse(events, safe=False)  # Return JSON for FullCalendar
#
#     # If not an AJAX request, render the page normally
#     return render(request, 'exercises/progress_tracking.html', {
#         'progress_data': progress_data,
#         'exercises': exercises,
#         'calendar_data': progress_data,
#         'current_week_start': start_of_week
#     })


# def add_progress(request):
#     connection = get_db_connection('add_progress')
#     if request.method == 'POST':
#         try:
#             if 'exerciseId' in request.POST:
#                 print(request.POST['exerciseId'])
#             else:
#                 print("exerciseId not in POST")
#             fname = request.session.get('fname')
#             lname = request.session.get('lname')
#             user_id = get_user_id_by_name(fname, lname)
#             exercise_id = request.POST.get('exerciseId')
#             date_completed = request.POST.get('dateCompleted')
#             sets = request.POST.get('setsCompleted')
#             reps = request.POST.get('repsCompleted')
#             duration = request.POST.get('duration')
#             calories = request.POST.get('caloriesBurned')
#
#             # More robust validation and conversion:
#             required_fields = {
#                 'exerciseId': exercise_id,
#                 'dateCompleted': date_completed,
#                 'setsCompleted': sets,
#                 'repsCompleted': reps,
#                 'duration': duration,
#                 'caloriesBurned': calories,
#             }
#
#             for field_name, field_value in required_fields.items():
#                 if not field_value:
#                     messages.error(request,
#                                    f"{field_name.replace('Id', ' ').replace('Completed', '')} is required.")  # Improved error message
#                     return redirect('exercisesAppName:progress_tracking')
#
#             try:
#                 exercise_id = int(exercise_id)  # Convert exercise_id to integer *after* checking if it's empty
#                 sets = int(sets)
#                 reps = int(reps)
#                 duration = float(duration)
#                 calories = float(calories)
#             except ValueError:
#                 messages.error(request, "Invalid numeric input. Please check all number fields.")
#                 return redirect('exercisesAppName:progress_tracking')
#             with connection.cursor() as cursor:  # Use a context manager for the cursor
#                 sql = """
#                     INSERT INTO ProgressTracking (userId, exerciseId, dateCompleted, setsCompleted, repsCompleted, duration, caloriesBurned)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """
#                 values = [user_id, exercise_id, date_completed, sets, reps, duration, calories]
#
#                 print("SQL Query:", sql % tuple(values))  # Print the query with values
#
#                 cursor.execute(sql, values)
#                 connection.commit()  # Commit the changes!
#
#                 messages.success(request, "Progress added successfully!")
#
#         except Exception as e:
#             messages.error(request, f"An error occurred: {str(e)}")
#             return redirect('exercisesAppName:progress_tracking')
#
#     return redirect('exercisesAppName:progress_tracking')
# def add_progress(request):
#     if request.method == 'POST':
#         try:
#             connection = get_db_connection('add_progress')
#             fname = request.session.get('fname')
#             lname = request.session.get('lname')
#             user_id = get_user_id_by_name(fname, lname)
#
#             exercise_id = request.POST.get('exerciseId')
#             date_completed = request.POST.get('dateCompleted')
#             sets = request.POST.get('setsCompleted')
#             reps = request.POST.get('repsCompleted')
#             duration = request.POST.get('duration')
#             calories = request.POST.get('caloriesBurned')
#
#             # Validation
#             if not all([exercise_id, date_completed, sets, reps, duration, calories]):
#                 return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
#
#             try:
#                 exercise_id = int(exercise_id)
#                 sets = int(sets)
#                 reps = int(reps)
#                 duration = float(duration)
#                 calories = float(calories)
#             except ValueError:
#                 return JsonResponse({'success': False, 'error': 'Invalid numeric input.'}, status=400)
#
#             with connection.cursor() as cursor:
#                 sql = """
#                     INSERT INTO ProgressTracking (userId, exerciseId, dateCompleted, setsCompleted, repsCompleted, duration, caloriesBurned)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """
#                 cursor.execute(sql, [user_id, exercise_id, date_completed, sets, reps, duration, calories])
#                 connection.commit()
#
#             return JsonResponse({'success': True})
#
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#
#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def delete_progress(request, progress_id):
    connection = get_db_connection('delete_progress')
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ProgressTracking WHERE id = %s", [progress_id])
    return redirect('exercisesAppName:progress_tracking')
# def fetch_exercises():
#     connection = get_db_connection('fetch_exercises')
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT id, name_of_exercise FROM Exercise")
#         return cursor.fetchall()


# @login_required
# # @login_required
# def add_progress(request):
#     connection = get_db_connection('add_progress')
#     if request.method == 'POST':
#         user_id = request.user.id
#         exercise_id = request.POST['exerciseId']
#         date_completed = request.POST['dateCompleted']
#         sets = request.POST['setsCompleted']
#         reps = request.POST['repsCompleted']
#         duration = request.POST['duration']
#         calories = request.POST['caloriesBurned']
#
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO ProgressTracking (userId, exerciseId, dateCompleted, setsCompleted, repsCompleted, duration, caloriesBurned)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, [user_id, exercise_id, date_completed, sets, reps, duration, calories])
#
#         return redirect('exercisesAppName:progress_tracking')


def add_progress(request):
    connection = get_db_connection('add_progress')
    if request.method == 'POST':
        try:
            fname = request.session.get('fname')
            lname = request.session.get('lname')
            user_id = get_user_id_by_name(fname, lname)
            exercise_id = request.POST.get('exerciseId')
            date_completed = request.POST.get('dateCompleted')
            sets = request.POST.get('setsCompleted')
            reps = request.POST.get('repsCompleted')
            duration = request.POST.get('duration')
            calories = request.POST.get('caloriesBurned')

            # Basic validation
            if not all([exercise_id, date_completed, sets, reps, duration, calories]):
                messages.error(request, "All fields are required.")
                return redirect('exercisesAppName:progress_tracking')

            # Convert numerical values safely
            try:
                sets = int(sets)
                reps = int(reps)
                duration = float(duration)
                calories = float(calories)
            except ValueError:
                messages.error(request, "Invalid numeric input.")
                return redirect('exercisesAppName:progress_tracking')

            # Insert data into ProgressTracking
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ProgressTracking (userId, exerciseId, dateCompleted, setsCompleted, repsCompleted, duration, caloriesBurned)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [user_id, exercise_id, date_completed, sets, reps, duration, calories])
                connection.commit()
            messages.success(request, "Progress added successfully!")
            return redirect('exercisesAppName:progress_tracking')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('exercisesAppName:progress_tracking')

    return redirect('exercisesAppName:progress_tracking')




