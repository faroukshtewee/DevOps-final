from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .utils.db_connection import get_db_connection
from accounts.views import get_user_id_by_name
from django.http import JsonResponse
from django.shortcuts import render
from datetime import date, datetime, timedelta


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
    # print(f'user_id-----------------------------------------\n{user_id}')
    search_query = request.GET.get("q", "")  # Get search query from URL
    exercises = []

    if search_query:
        exercises = search_exercises(search_query)
        # print(f'exercises-----------------------------------------\n{exercises}')
        if not exercises:  # Handle case where no exercises match the search query
            return HttpResponse("No exercises found for the given search query", status=404)

    else:
        exercises = get_recommendations_with_exercise_details(user_id)
        # print(f'exercises-----------------------------------------\n{exercises}')
        if not exercises:  # Check if no exercises were returned
            return HttpResponse("No exercises found", status=404)

    return render(request, 'exercises/exercises_list.html', {'exercises': exercises, 'query': search_query})


def search_exercises(query):
    conn = get_db_connection('search_exercises')
    cursor = conn.cursor(dictionary=True)

    # First, try to find an exact match
    exact_sql = """
    SELECT DISTINCT name_of_exercise, `Desc`, `Type`,`linkForImage`, `level` AS exercise_level
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
    SELECT DISTINCT name_of_exercise, `Desc`, `Type`,`linkForImage`, `level`AS exercise_level
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


def delete_progress(request, progress_id):
    connection = get_db_connection('delete_progress')
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ProgressTracking WHERE id = %s", [progress_id])
    return redirect('exercisesAppName:progress_tracking')


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
