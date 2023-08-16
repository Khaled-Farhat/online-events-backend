import pytest


@pytest.fixture
def get_talk_representation(get_datetime_representation):
    def get_talk_representation(
        talk,
        include_id=False,
        include_speaker=False,
        include_event=False,
        include_status=False,
    ):
        representation = {
            "title": talk.title,
            "start": get_datetime_representation(talk.start),
            "end": get_datetime_representation(talk.end),
        }
        if include_id:
            representation["id"] = talk.pk
        if include_speaker:
            representation["speaker"] = talk.speaker.username
        if include_event:
            representation["event"] = talk.event.id
        if include_status:
            representation["status"] = talk.status
        return representation

    return get_talk_representation
