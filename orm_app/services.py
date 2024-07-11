from collections import defaultdict

from django.db.models import Count, OuterRef, Subquery

from .models import AskUser, Container, Product, Review, Sale, User

from django.db.models import Avg


def get_review_statistics_by_container(container_id) -> dict:
    review_statistics = {}

    # Retrieve all products in the specified container
    products = Product.objects.filter(sale__container__id=container_id).distinct()

    # Iterate over each product to get review statistics
    for product in products:
        # Fetch review counts for each rating category
        review_counts = (
            Review.objects.filter(product=product)
            .values("rating")
            .annotate(count=Count("rating"))
        )

        # Fetch users who gave reviews for this product
        reviewers = User.objects.filter(review__product=product).distinct()

        # Initialize a dictionary to store reviewer information
        reviewers_info = defaultdict(list)

        # Iterate over each reviewer to get their reviews for this product
        for reviewer in reviewers:
            reviews_by_reviewer = Review.objects.filter(product=product, user=reviewer)
            for review in reviews_by_reviewer:
                reviewers_info[reviewer.name].append(review.rating)

        # Store review statistics and reviewer information in the dictionary
        review_statistics[product.name] = {
            "reviews": {
                review_count["rating"]: review_count["count"]
                for review_count in review_counts
            },
            "reviewers": {
                reviewer.name: reviewers_info[reviewer.name] for reviewer in reviewers
            },
        }

    return review_statistics


def get_reviewers_statistics_by_user(reviewer_pk) -> dict:
    # Get the user's reviews along with product and rating information
    reviews_info = Review.objects.filter(user_id=reviewer_pk).select_related("product")

    # Initialize statistics dictionary
    statistics = {
        "total_reviews": 0,
        "excellent_reviews": 0,
        "medium_reviews": 0,
        "bad_reviews": 0,
        "product_ratings": {},  # Dictionary to store product ratings by the user
    }

    # Populate product ratings for each review
    for review in reviews_info:
        product_name = review.product.name if review.product else "Unknown Product"
        rating = review.rating
        statistics["total_reviews"] += 1

        # Update rating count
        if rating == Review.EXCELLENT:
            statistics["excellent_reviews"] += 1
        elif rating == Review.MEDIUM:
            statistics["medium_reviews"] += 1
        elif rating == Review.BAD:
            statistics["bad_reviews"] += 1

        # Update product ratings dictionary
        if product_name not in statistics["product_ratings"]:
            statistics["product_ratings"][product_name] = {
                "excellent": 0,
                "medium": 0,
                "bad": 0,
            }
        statistics["product_ratings"][product_name][rating.lower()] += 1

    return statistics



def get_products_statistics_by_date(from_date, to_date) -> dict:
    review_statistics = {}
    containers = Container.objects.filter(arrival_date__range=[from_date, to_date])
    review_statistics = {}
    review_statistics = {}

def asked_users_count(request):
    return {
        'asked_users_count': AskUser.objects.count(),
    }
    
def get_product_reviews_statistics_by_pk(product_pk):
    reviews = Review.objects.filter(product_id=product_pk, is_active=True)
    total_reviews = reviews.count()
    reviewers = reviews.values_list('user__name', flat=True).distinct()
    average_rating = reviews.aggregate(average_rating=Avg('numerical_rating'))['average_rating']
    excellent_reviews = reviews.filter(rating=Review.EXCELLENT).count()
    medium_reviews = reviews.filter(rating=Review.MEDIUM).count()
    bad_reviews = reviews.filter(rating=Review.BAD).count()
    
    return {
        'total_reviews': total_reviews,
        'reviewers': list(reviewers),
        'average_rating': average_rating,
        'excellent_reviews': excellent_reviews,
        'medium_reviews': medium_reviews,
        'bad_reviews': bad_reviews,
        'details': reviews,
    }