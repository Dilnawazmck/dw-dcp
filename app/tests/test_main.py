import mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import (
    TEST_DUMMY_TOKEN,
    TEST_TOKEN_AUTH_ACCESS,
    TEST_TOKEN_CLIENT_LIST,
)
from app.db.session import get_db_session
from app.main import app
from app.schemas import user_modal as user_modal_schema
from app.services import authentication
from app.services.user_modal import _user_modal
from app.tests.conftest import (
    get_test_db_session,
    override_get_current_user,
    override_verify_token,
    override_verify_token_via_okta,
)

client = TestClient(app)
app.dependency_overrides[get_db_session] = get_test_db_session
app.dependency_overrides[authentication.verify_token] = override_verify_token
app.dependency_overrides[
    authentication.verify_token_via_okta
] = override_verify_token_via_okta

mock.patch(
    "app.services.authentication.get_current_user",
    override_get_current_user,
).start()


def test_get_survey_excel():
    filename = "export.xlsx"
    response = client.get(
        "/api/response/40d4/export", headers={"Authorization": TEST_TOKEN_AUTH_ACCESS}
    )
    assert response.status_code == 200
    assert filename in response.headers["content-disposition"]


def test_read_main():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"data": "You are accessing text analytics API"}


class TestAuth:
    def test_get_access_and_refresh_token(self):
        response = client.get(
            "/api/auth/access-token",
            headers={"Authorization": TEST_TOKEN_AUTH_ACCESS},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) >= 0


class TestTopics:
    def test_topic_list_api(self):
        response = client.get(
            "/api/topics", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) >= 0


class TestPractices:
    def test_practice_list_api(self):
        response = client.get(
            "/api/practices", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) >= 0


class TestSentiment:
    def test_sentiment_api(self):
        response = client.get(
            "/api/sentiment", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) >= 0


class TestClient:
    def test_client_list_api(self):
        app.dependency_overrides[authentication.verify_token] = override_verify_token
        response = client.get(
            "/api/client", headers={"Authorization": TEST_TOKEN_CLIENT_LIST}
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) == 1
        assert json_resp[0].get("name") == "TestClient1"
        assert isinstance(json_resp[0].get("surveys"), list)
        assert json_resp[0].get("surveys")[0]["name"] == "TestSurvey1"
        assert json_resp[0].get("surveys")[0]["type"] == 1


class TestSentimentCount:
    def test_get_sentiment_count(self):
        response = client.get(
            "/api/response/40d4/sentiment-count?group_by=practice_id&filters=practice_id:eq:1;sentiment_id:eq:1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) == 1
        assert json_resp[0].get("practice_id") == 1

    def test_sentiment_breakdown(self):
        response = client.get(
            "/api/response/40d4/sentiment-breakdown",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) == 3

    def test_sentiment_wise_demographics(self):
        response = client.get(
            "/api/response/40d4/sentiment-wise-demographic?demographic=overall&sentiment=Positive&orderby=desc&nsize=gt:0&page=1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) > 0

    def test_sentiment_mention_matrix(self):
        response = client.get(
            "/api/response/40d4/sentiment-mention-matrix?group_by=practice_id",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) > 0

    def test_demographic_heatmap(self):
        response = client.get(
            "/api/response/40d4/demographic-heatmap?demographic=demo_BU&group_by=practice_id&page_no=1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) > 0


class TestSurvey:
    def test_get_survey_questions(self):
        response = client.get(
            "/api/survey/40d4/questions?survey_type=1", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) >= 0


class TestUserSavedComment:
    def test_save_comment(self):
        response = client.post(
            "/api/user-comment/",
            headers={"Authorization": TEST_DUMMY_TOKEN},
            json={"response_id": 1, "folder_name": "test_folder"},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert json_resp.get("response_id") == 1

    def test_get_user_folder_list(self):
        response = client.get(
            "/api/user-comment/folder-list?survey_id=40d4&survey_type=1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert len(json_resp) > 0


class TestFeedback:
    def test_verify_feedback_categories_api(self):
        response = client.get(
            "/api/feedback/categories", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        print(response.json())
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # def test_verify_post_feedback_api(self):
    #     response = client.post(url="/api/feedback/",
    #                            data=json.dumps({
    #                                "response_id": 1,
    #                                "feedback_category_id": 1,
    #                                "description": "test"
    #                            })
    #                            )
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)


class TestResponse:
    def test_verify_popular_words_api(self):
        response = client.get(
            "/api/response/40d4/popular-words?group_by=topic_id",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 0

    def test_verify_counts_api(self):
        response = client.get(
            "/api/response/40d4/counts?group_by=topic_id",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp.get("total_comments") >= 0
        assert isinstance(resp.get("data"), list)

    def test_verify_comments_api(self):
        response = client.get(
            "/api/response/40d4/comments", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        assert len(response.json()) >= 0

    def test_verify_wordcloud_api(self):
        response = client.get(
            "/api/response/40d4/wordcloud", headers={"Authorization": TEST_DUMMY_TOKEN}
        )
        assert response.status_code == 200
        assert len(response.json()) >= 0


# class TestUtils:
# def test_verify_similar_words_api(self):
#     response = client.get(
#         "/api/similar?keywords=play",
#         headers={"Authorization": TEST_DUMMY_TOKEN},
#     )
#     assert response.status_code == 200
#     resp = response.json()
#     assert isinstance(resp, list)
#     assert len(resp) == 5

# def test_verify_classify_api(self):
#     response = client.post(
#         "/api/classify",
#         json={
#             "text": ["I want to be a pilot"],
#             "labels": [
#                 "emotion",
#                 "career",
#                 "culture",
#                 "passion",
#                 "life",
#                 "philosophy",
#             ],
#         },
#         headers={"Authorization": TEST_DUMMY_TOKEN},
#     )
#     assert response.status_code == 200
#     resp = response.json()
#     assert resp.get("sequence") == "I want to be a pilot"
#     assert resp.get("labels")[0] == "career"
#     assert len(resp.get("scores")) == 6


class TestUserSurveyPreset:
    def test_insert_user_survey_preset(self):
        d1 = [{"name": "standard"}]

        response = client.post(
            url="/api/survey/40d4/user-preset?name=Test1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
            json=d1,
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_get_user_survey_preset(self):
        response = client.get(
            url="/api/survey/40d4/user-preset",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 0

    def test_edit_preset(self):
        response = client.put(
            url="/api/survey/40d4/user-preset/1",
            json=[{"name": "updated"}],
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_delete_preset(self):
        response = client.delete(
            url="/api/survey/40d4/user-preset/1",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}


class TestCustomTopicsJob:
    def test_get_user_topics_job_status(self):
        response = client.get(
            url="/api/custom-topics-job/status?survey_id=40d4",
            headers={"Authorization": TEST_DUMMY_TOKEN},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 0
        resp = response.json()
        assert resp["status"] == "queue"


class TestUserModal:
    def test_insert_user_modal_status(self):
        db: Session = next(get_test_db_session())
        obj_in = user_modal_schema.UserModalIn(user_id=1, show_modal=True,show_classify_modal=True)
        response = _user_modal.create(db=db, obj_in=obj_in)
        assert response.user_id > 0

    def test_get_user_modal_status(self):
        db: Session = next(get_test_db_session())
        result = _user_modal.get_user_modal_status(db=db, user_id=1)
        assert result[0] is True


#
# class TestUserTopics:
#     def test_create_user_topics_api(self):
#         d1 = [{'name': 'shared vision', 'type': 'practice'}, {'name': 'covid19', 'type': 'standard'}]
#
#         response = client.post(
#             url="/api/survey/40d4/user-topics",
#             json=d1,
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 200
#         assert response.json() == {"message": "Your topics list has been added. Once you data has been re-processed "
#                                               "you will be notified via an email"}
#
#     def test_get_user_topics_api(self):
#         response = client.get("/api/survey/40d4/user-topics", headers={"Authorization": TEST_DUMMY_TOKEN})
#
#         assert response.status_code == 200
#         assert response.json() == {'topics': [{'name': 'shared vision', 'type': 'practice'}, {'name': 'covid19',
#                                                                                               'type': 'standard'},
#                                               {"name": "Unclassified", "type": "standard"}]}
#
#     def test_edit_user_topics_api(self):
#         d1 = [{'name': 'Strategic clarity', 'type': 'practice'}, {'name': 'communication', 'type': 'standard'}]
#         response = client.put(
#             url="/api/survey/40d4/user-topics",
#             json=d1,
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 400
#
#         db: Session = next(get_test_db_session())
#         db.query(CustomTopicsJob).filter(CustomTopicsJob.status == CustomTopicsJobStatus.QUEUE.value).\
#             update({"status": CustomTopicsJobStatus.COMPLETE.value})
#         db.commit()
#
#         response = client.put(
#             url="/api/survey/40d4/user-topics",
#             json=d1,
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 200
#         assert response.json() == {"message": "Your topics list has been updated successfully. Once you data has "
#                                               "been re-processed you will be notified via an email"}
#
#     def test_get_counts_in_survey_by_user_topics(self):
#         response = client.get(
#             url="/api/response/40d4/user-topics-counts",
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 200
#         resp = response.json()
#         assert resp.get("total_comments") >= 0
#         assert isinstance(resp.get("data"), list)
#
#     def test_get_popular_words_by_user_topics(self):
#         response = client.get(
#             url="/api/response/40d4/user-topics-popular-words",
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 200
#         assert len(response.json()) >= 0
#
#     def test_get_user_topics_comments(self):
#         response = client.get(
#             url="/api/response/40d4/user-topics-comments",
#             headers={"Authorization": TEST_DUMMY_TOKEN}
#         )
#
#         assert response.status_code == 200
#         assert len(response.json()) >= 0
