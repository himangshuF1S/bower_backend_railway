import random
import uuid
import string
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Session, Course
from calendars.serializers import SessionSerializer

User = get_user_model()

class SessionView(APIView):
    """
    API View to fetch sessions for the current authenticated user 
    based on type of meeting, time period, and event type filters.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles GET requests to retrieve filtered sessions.

        Query Parameters:
        - type_of_meet: str (mentor/my_events) [default: mentor]
        - period: str (day/week/month) [default: month]
        - event_types: list of event types [default: all event types]
        - current_date: str (YYYY-MM-DD) received from FE [default: today]
        - current_time: str (HH:MM:SS) received from FE [default: now]

        Returns:
        - JSON response containing session details within the requested period.
        """

        # Extract request parameters
        type_of_meet = request.query_params.get("type_of_meet", "mentor")
        period = request.query_params.get("period", "month")
        event_types = request.query_params.getlist("event_types", [])  # List of event types
        current_user = request.user

        # Get current_date from FE, default to today if not provided
        current_date = request.query_params.get("current_date")
        # if current_date:
        #     try:
        #         current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        #     except ValueError:
        #         return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        # else:
        #     current_date = datetime.now().date()

        # Get current_time from FE, default to now if not provided
        current_time = request.query_params.get("current_time")
        # if current_time:
        #     try:
        #         current_time = make_aware(datetime.strptime(current_time, "%H:%M:%S"))
        #     except ValueError:
        #         return Response({"error": "Invalid time format. Use HH:MM:SS"}, status=400)
        # else:
        #     current_time = datetime.now()

        # Determine the time range based on period
        if period == "day":
            start_date = current_date
            end_date = current_date
        elif period == "week":
            start_date = current_date - timedelta(days=current_date.weekday())  # Start of the week (Monday)
            end_date = start_date + timedelta(days=6)  # End of the week (Sunday)
        else:  # Default to "month"
            start_date = current_date.replace(day=1)  # Start of the month
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)  # First day of next month
            end_date = next_month - timedelta(days=1)  # Last day of this month

        # Fetch sessions based on the given filters
        sessions = self.get_sessions(start_date, end_date, type_of_meet, current_user, event_types)

        # Serialize the data
        serializer = SessionSerializer(sessions, many=True)

        # Response Format
        response_data = {
            "current_date": str(current_date),
            "current_time": str(current_time.time()),  # Send only HH:MM:SS
            "start_date": str(start_date),
            "end_date": str(end_date),
            "sessions": serializer.data
        }
        return Response(response_data)

    def get_sessions(self, start_date, end_date, type_of_meet, current_user, event_types):
        """
        Fetches sessions based on filters for type_of_meet, period, and event types.

        Parameters:
        - start_date: Start date for filtering sessions
        - end_date: End date for filtering sessions
        - type_of_meet: "mentor" or "my_events"
        - current_user: The logged-in user
        - event_types: List of event types to filter

        Returns:
        - QuerySet of filtered sessions
        """

        # Base Query: Sessions occurring within the specified period
        sessions = Session.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )

        # Filter by type_of_meet
        if type_of_meet == "mentor":
            sessions = sessions.filter(created_by_mentor=True)
        elif type_of_meet == "my_events":
            sessions = sessions.filter(created_by=current_user, created_by_mentor=False)

        # Filter by event_types if provided
        if event_types:
           sessions = sessions.filter(event_type__in=event_types)

        return sessions

def generate_random_string(length=5):
    """Generates a random string of given length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class CreateSessionView(APIView):
    """
    API View to create a new session while ensuring required validations and business logic.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST request to create a new session.

        Required Fields:
        - title: str
        - start_date: date (YYYY-MM-DD)
        - start_time: time (HH:MM)
        - end_time: time (HH:MM)

        Optional Fields:
        - course: UUID (nullable, must exist in Course table if provided)
        - description: str (nullable)
        - end_date: date (nullable)
        - mode: "online" or "offline" (default: online)
        - meet_link: str (nullable, generates a random string if not provided)
        - participants: JSON list of user IDs (only valid, non-admin, unique users are added)
        - event_type: str (nullable)
        - recurring_type: str (nullable)
        - updated_by: User (nullable)

        Business Logic:
        - If `course` is provided, `created_by = course.mentor`
        - If `course` is null, `created_by = current_user`
        - If `course` is provided, `created_by_mentor = True`, else `False`
        - If `meet_link` is null, generates a random 5-character string
        """

        data = request.data
        current_user = request.user

        # Required Fields Validation
        required_fields = ["title", "start_date", "start_time", "end_time"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle Course and Created By logic
        course = data.get("course")
        created_by_mentor = False

        if course:
            try:
                course_obj = Course.objects.get(id=course)
                created_by = course_obj.mentor  # Assign course mentor
                created_by_mentor = True
            except Course.DoesNotExist:
                return Response({"error": "Invalid course ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            created_by = current_user  # Assign current user if no course is given

        # Handle Participants
        participants = []
        participant_ids = data.get("participants", [])
        if isinstance(participant_ids, list):
            valid_participants = User.objects.filter(id__in=participant_ids, is_admin=False).distinct()
            participants = list(valid_participants)  # Convert QuerySet to list of users

        # Handle Meet Link (Generate random if null)
        meet_link = data.get("meet_link", None) or generate_random_string(5)

        # Create Session Object
        session = Session.objects.create(
            id=uuid.uuid4(),
            course=course_obj if course else None,
            title=data["title"],
            description=data.get("description"),
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            start_time=data["start_time"],
            end_time=data["end_time"],
            mode=data.get("mode", "online"),  # Default to "online"
            meet_link=meet_link,
            created_by=created_by,
            created_by_mentor=created_by_mentor,
            updated_by_id=data.get("updated_by"),
            event_type=data.get("event_type"),
            recurring_type=data.get("recurring_type"),
            created_at=now(),
            updated_at=now()
        )

        # Add Participants
        session.participants.set(participants)

        # Serialize and Return Response
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
