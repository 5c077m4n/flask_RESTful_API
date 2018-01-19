from flask import jsonify, Blueprint, abort, g, make_response
from flask_restful import (
    Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for
)

import models
from auth import auth


review_fields = {
    'id': fields.Integer,
    'for_course': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'created_at': fields.DateTime
}

def review_or_404(review_id):
    """Check to see if the review ID exists or abort.
    """
    try:
        review = models.Review.get(models.Review.id == review_id)
    except models.Review.DoesNotExist:
        abort(404)
    else:
        return review

def add_course(review):
    review.for_course = url_for('resources.courses.cource', id = review.course.id)
    return review

class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            type = inputs.positive,
            required = True,
            help = 'No course has been provided',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'rating',
            type = inputs.int_range(1, 5),
            required = True,
            help = 'No rating has been provided',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'comment',
            required = False,
            nullable = True,
            default = '',
            location = ['form', 'json']
        )
        super().__init__()

    def get(self):
        return jsonify({'reviews': [{'course': 1, 'rating': 5}]})

    @auth.login_required
    @marshal_with(review_fields)
    def post(self):
        args = self.reqparse.parse_args()
        review = models.Review.create(
            **args, created_by = g.user
        )
        return add_course(review)


class Review(Resource):
    @marshal_with(review_fields)
    def get(self, id):
        return add_course(review_or_404(id))

    @auth.login_required
    @marshal_with(review_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(
                jsonify({
                        'error':
                        'This review is either not editable or does noe exist.'
                    }), 403
            )
        review.update(**args).execute()
        review = add_course(review_or_404(id))
        return (
            review, 200, {'Location': url_for('resource.reviews.review', id = id)}
        )

    @auth.login_required
    def delete(self, id):
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(
                jsonify({
                        'error':
                        'This review is either not editable or does noe exist.'
                    }), 403
            )
        review.delete().execute()
        return (
            '', 204, {'Location': url_for('resorces.reviews.reviews')}
        )


reviews_api = Blueprint('resources.reviews', __name__)
api = Api(reviews_api)
api.add_resource(
    ReviewList,
    '/reviews',
    endpoint = 'reviews'
)
api.add_resource(
    Review,
    '/reviews/<int:id>',
    endpoint = 'review'
)
