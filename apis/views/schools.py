
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apis.models import SchoolStructure, Schools, Classes, Personnel, Subjects, StudentSubjectsScore
from django.db.models import Case, When, CharField, Value
from collections import defaultdict
from django.db.models import Prefetch


class StudentSubjectsScoreAPIView(APIView):

    @staticmethod
    def post(request, *args, **kwargs):
        """
        [Backend API and Data Validations Skill Test]

        description: create API Endpoint for insert score data of each student by following rules.

        rules:      - Score must be number, equal or greater than 0 and equal or less than 100.
                    - Credit must be integer, greater than 0 and equal or less than 3.
                    - Payload data must be contained `first_name`, `last_name`, `subject_title` and `score`.
                        - `first_name` in payload must be string (if not return bad request status).
                        - `last_name` in payload must be string (if not return bad request status).
                        - `subject_title` in payload must be string (if not return bad request status).
                        - `score` in payload must be number (if not return bad request status).

                    - Student's score of each subject must be unique (it's mean 1 student only have 1 row of score
                            of each subject).
                    - If student's score of each subject already existed, It will update new score
                            (Don't created it).
                    - If Update, Credit must not be changed.
                    - If Data Payload not complete return clearly message with bad request status.
                    - If Subject's Name or Student's Name not found in Database return clearly message with bad request status.
                    - If Success return student's details, subject's title, credit and score context with created status.

        remark:     - `score` is subject's score of each student.
                    - `credit` is subject's credit.
                    - student's first name, lastname and subject's title can find in DATABASE (you can create more
                            for test add new score).

        """

        request_data = request.data

        # Validate payload completeness
        required_fields = ["first_name", "last_name", "subject_title", "score"]
        if not all(field in request.data for field in required_fields):
            return Response("Missing one or more required fields.", status=status.HTTP_400_BAD_REQUEST)

        # Validate data types and value constraints
        if not isinstance(request_data.get("first_name"), str) or not isinstance(request_data.get("last_name"), str):
            return Response("First name and last name must be strings.", status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(request_data.get("subject_title"), str):
            return Response("Subject title must be a string.", status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(request_data.get("score"), (int, float)) or not 0 <= request_data.get("score") <= 100:
            return Response("Score must be a number between 0 and 100.", status=status.HTTP_400_BAD_REQUEST)

        # Since credit is not always provided, we need to handle its absence gracefully
        credit = request_data.get("credit")
        if credit is not None:
            try:
                credit = int(credit)
                if not 1 <= credit <= 3:
                    raise ValueError()
            except ValueError:
                return Response("Credit must be an integer between 1 and 3.", status=status.HTTP_400_BAD_REQUEST)

        # Validate and lookup the subject and student
        try:
            subject = Subjects.objects.get(title=request_data["subject_title"])
            student = Personnel.objects.get(
                first_name=request_data["first_name"], last_name=request_data["last_name"], personnel_type=2)  # Assuming 2 denotes students
        except (Subjects.DoesNotExist, Personnel.DoesNotExist) as e:
            return Response(f"{str(e)} not found.", status=status.HTTP_400_BAD_REQUEST)

        # Check if score entry exists to decide on creation or update
        student_subject_score, created = StudentSubjectsScore.objects.get_or_create(
            student=student,
            subjects=subject,
            defaults={'score': request_data["score"]}
        )

        if not created and credit is None:
            # If updating, only update score if credit not provided in request
            student_subject_score.score = request_data["score"]
            student_subject_score.save(update_fields=["score"])
        elif not created and credit is not None:
            # If updating and credit provided, it indicates an incorrect request as credit should not change
            return Response("Credit cannot be changed.", status=status.HTTP_400_BAD_REQUEST)

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({
            "message": "Created" if created else "Updated",
            "student": f"{student.first_name} {student.last_name}",
            "subject": subject.title,
            "credit": student_subject_score.credit,  # This remains unchanged on update
            "score": student_subject_score.score
        }, status=response_status)


class StudentSubjectsScoreDetailsAPIView(APIView):

    """
    [Backend API and Data Calculation Skill Test]

    description: get student details, subject's details, subject's credit, their score of each subject,
                their grade of each subject and their grade point average by student's ID.

    pattern:     Data pattern in 'context_data' variable below.

    remark:     - `grade` will be A  if 80 <= score <= 100
                                    B+ if 75 <= score < 80
                                    B  if 70 <= score < 75
                                    C+ if 65 <= score < 70
                                    C  if 60 <= score < 65
                                    D+ if 55 <= score < 60
                                    D  if 50 <= score < 55
                                    F  if score < 50

    """

    @staticmethod
    def get_grade(score):
        if score >= 80:
            return 'A'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'D+'
        elif score >= 50:
            return 'D'
        else:
            return 'F'

    @staticmethod
    def grade_to_point(grade):
        grade_points = {
            'A': 4.0,
            'B+': 3.5,
            'B': 3.0,
            'C+': 2.5,
            'C': 2.0,
            'D+': 1.5,
            'D': 1.0,
            'F': 0.0,
        }
        # Default to 0.0 if grade is not found
        return grade_points.get(grade, 0.0)

    @staticmethod
    def get(request, *args, **kwargs):
        student_id = kwargs.get("id", None)

        try:
            student = Personnel.objects.get(pk=student_id)
            scores = StudentSubjectsScore.objects.filter(student=student)

            subject_details = []
            for score in scores:
                grade = StudentSubjectsScoreDetailsAPIView.get_grade(
                    score.score)
                subject_details.append({
                    "subject": score.subjects.title,
                    "credit": score.credit,
                    "score": score.score,
                    "grade": grade,
                })

            # Calculate the GPA based on the grade points
            total_points = sum(StudentSubjectsScoreDetailsAPIView.grade_to_point(
                detail['grade']) for detail in subject_details)
            gpa = total_points / len(subject_details) if subject_details else 0

            context_data = {
                "student": {
                    "id": student.id,
                    "full_name": f"{student.first_name} {student.last_name}",
                    "school": student.school_class.school.title,
                },
                "subject_detail": subject_details,
                "grade_point_average": round(gpa, 2),
            }

            return Response(context_data, status=status.HTTP_200_OK)
        except Personnel.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


class PersonnelDetailsAPIView(APIView):

    """
        [Basic Skill and Observational Skill Test]

        description: get personnel details by school's name.

        data pattern:  {order}. school: {school's title}, role: {personnel type in string}, class: {class's order}, name: {first name} {last name}.

        result pattern : in `data_pattern` variable below.

        example:    1. school: Rose Garden School, role: Head of the room, class: 1, name: Reed Richards.
                    2. school: Rose Garden School, role: Student, class: 1, name: Blackagar Boltagon.

        rules:      - Personnel's name and School's title must be capitalize.
                    - Personnel's details order must be ordered by their role, their class order and their name.

        """

    def get(self, request, *args, **kwargs):
        # Accessing school_title from URL parameter
        school_title = kwargs.get("school_title", None)

        if not school_title:
            return Response({"error": "School title is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            personnel = Personnel.objects.filter(
                school_class__school__title__iexact=school_title
            ).annotate(
                role=Case(
                    When(personnel_type=0, then=Value('Teacher')),
                    When(personnel_type=1, then=Value('Head of the room')),
                    When(personnel_type=2, then=Value('Student')),
                    default=Value('Unknown'),
                    output_field=CharField(),
                )
            ).order_by('role', 'school_class__class_order', 'first_name', 'last_name')

            if not personnel:
                return Response({"error": "No personnel found for the given school."}, status=status.HTTP_404_NOT_FOUND)

            your_result = [
                f"{index + 1}. school: {p.school_class.school.title}, role: {p.role}, class: {p.school_class.class_order}, name: {p.first_name} {p.last_name}"
                for index, p in enumerate(personnel)
            ]

            return Response(your_result, status=status.HTTP_200_OK)

        except Schools.DoesNotExist:
            return Response({"error": "School not found."}, status=status.HTTP_404_NOT_FOUND)


def get_personnel_role_display(personnel_type):
    role_mapping = {
        0: "Teacher",
        1: "Head of the room",
        2: "Student",
    }
    return role_mapping.get(personnel_type, "Unknown")


class SchoolHierarchyAPIView(APIView):

    """
    [Logical Test]

    description: get personnel list in hierarchy order by school's title, class and personnel's name.

    pattern: in `data_pattern` variable below.

    """

    def get(self, request, *args, **kwargs):
        # Start by getting all schools, ordered by title
        schools = Schools.objects.prefetch_related(
            Prefetch('classes_set',
                     queryset=Classes.objects.prefetch_related(
                         Prefetch('personnel_set',
                                  queryset=Personnel.objects.order_by(
                                      'personnel_type', 'first_name', 'last_name'),
                                  to_attr='personnel_list')
                     ).order_by('class_order'),
                     to_attr='classes_list')
        ).order_by('title')

        hierarchy_data = []

        for school in schools:
            school_entry = {"school": school.title, "details": []}

            # Default dictionary to hold classes and their personnel
            class_personnel = defaultdict(lambda: defaultdict(list))

            for cls in school.classes_list:
                for person in cls.personnel_list:
                    role = "Teacher" if person.personnel_type == 0 else \
                           "Head of the room" if person.personnel_type == 1 else \
                           "Student"

                    # For teachers, their name becomes a key, for others, they are added to the list
                    if role == "Teacher":
                        teacher_key = f"{role}: {person.first_name} {person.last_name}"
                        # Ensure the teacher key exists
                        if teacher_key not in class_personnel[f"class {cls.class_order}"]:
                            class_personnel[f"class {cls.class_order}"][teacher_key] = [
                            ]
                    else:
                        # Find the correct teacher to append this personnel under
                        for teacher_key in class_personnel[f"class {cls.class_order}"].keys():
                            class_personnel[f"class {cls.class_order}"][teacher_key].append(
                                {role: f"{person.first_name} {person.last_name}"})

            # Convert the default dictionary to the format required by 'details'
            for class_order, personnel in class_personnel.items():
                class_entry = {class_order: {}}
                for teacher, people in personnel.items():
                    class_entry[class_order][teacher] = people
                school_entry["details"].append(class_entry)

            hierarchy_data.append(school_entry)

        return Response(hierarchy_data, status=status.HTTP_200_OK)


class SchoolStructureAPIView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):
        """
        [Logical Test]

        description: get School's structure list in hierarchy.

        pattern: in `data_pattern` variable below.

        """

        # Fetch all school structure entries
        all_structures = SchoolStructure.objects.all().select_related('parent')

        # Create a map of parent ID to children
        parent_map = {}
        for structure in all_structures:
            if structure.parent_id not in parent_map:
                parent_map[structure.parent_id] = []
            parent_map[structure.parent_id].append(structure)

        # Function to build hierarchy for a given parent ID
        def build_hierarchy(parent_id):
            hierarchy = []
            for child in parent_map.get(parent_id, []):
                node = {"title": child.title}
                # Check if the current node has children
                if child.id in parent_map:
                    node["sub"] = build_hierarchy(child.id)
                hierarchy.append(node)
            return hierarchy

        # Build hierarchy starting with root nodes (those without a parent)
        hierarchy_data = build_hierarchy(None)

        return Response(hierarchy_data, status=status.HTTP_200_OK)
