from fastapi import APIRouter

# from app.api.routes import (
#     admin,
#     authentication,
#     client,
#     feedback_category,
#     practice,
#     response,
#     survey,
#     topic,
#     user_saved_comment,
#     utils,
#     user_topics,
#     user_modal,
#     user_survey_preset,
#     custom_topics_job,
#     sentiment,
#     exclude_keywords
# )

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"data": "You are accessing text analytics API"}


# router.include_router(authentication.router, tags=["Authentication"], prefix="/auth")
# router.include_router(topic.router, tags=["Topics"], prefix="/topics")
# router.include_router(practice.router, tags=["Practices"], prefix="/practices")
# router.include_router(client.router, tags=["Clients"], prefix="/client")
# router.include_router(survey.router, tags=["Surveys"], prefix="/survey")
# router.include_router(response.router, tags=["Responses"], prefix="/response")
# router.include_router(utils.router, tags=["Others"])
# router.include_router(
#     feedback_category.router, prefix="/feedback", tags=["FeedbackCategories"]
# )
# router.include_router(
#     user_saved_comment.router, prefix="/user-comment", tags=["UserComments"]
# )
# router.include_router(admin.router, prefix="/admin", tags=["Admin"])
# router.include_router(user_topics.router, tags=["UserTopics"])
# router.include_router(custom_topics_job.router, tags=["CustomTopicsJob"])
# router.include_router(user_modal.router, prefix="/user_modal", tags=["User-Modal"])
# router.include_router(user_survey_preset.router, tags=["Preset"])
# router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])
# router.include_router(exclude_keywords.router, tags=["Exclude-Keywords"])
