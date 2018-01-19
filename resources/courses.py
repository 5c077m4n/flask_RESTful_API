from flask import jsonify, Blueprint, abort, make_response
from flask_restful import (
    Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for
)

import models
from auth import auth


course_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'reviews': fields.List(fields.String)
}

def add_reviews(course):
    """Add a review for a course.
    """
    course.reviews = [
        # for review in course.review_set:
        #     url_for('resources.reviews.review', id = review.id) 
        url_for('resources.reviews.review', id = review.id)
            for review in course.review_set
    ]
    return course

def course_or_404(course_id):
    """Check to see if the course ID exists or abort.
    """
    try:
        course = models.Course.get(models.Course.id == course_id)
    except models.Course.DoesNotExist:
        abort(404)
    else:
        return course


class CourseList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required = True,
            help = 'No course title provided',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required = True,
            help = 'No course URL provided',
            location = ['form', 'json'],
            type = inputs.url
        )
        super().__init__()

    def get(self):
        courses = [
            marshal(add_reviews(course), course_fields)
                for course in models.Course.select()
        ]
        return {'courses': courses}

    @auth.login_required
    @marshal_with(course_fields)
    def post(self):
        args = self.reqparse.parse_args()
        course = models.Course.create(**args)
        return (
            add_reviews(course), 201, {'location': url_for('resources.courses.course', id = course.id)}
        )


class Course(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required = True,
            help = 'No course title provided',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required = True,
            help = 'No course URL provided',
            location = ['form', 'json'],
            type = inputs.url
        )
        super().__init__()

    @marshal_with(course_fields)
    def get(self, id):
        return add_reviews(course_or_404(id))

    @auth.login_required
    @marshal_with(course_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        models.Course.update(**args).where(models.Course.id == id).execute()
        return (
            add_reviews(models.Course.get(models.Course.id == id)), 200,
            {'location': url_for('resources.courses.course', id = id)}
        )

    @auth.login_required
    def delete(self, id):
        course_or_404(id)
        models.Course.delete().where(models.Course.id == id).execute()
        return (
            '', 204, {'location': url_for('resources.courses.courses')}
        )

courses_api = Blueprint('resources.courses', __name__)
api = Api(courses_api)
api.add_resource(
    CourseList,
    '/api/v1/courses',
    endpoint = 'courses'
)
api.add_resource(
    Course,
    '/api/v1/courses/<int:id>',
    endpoint = 'course'
)
