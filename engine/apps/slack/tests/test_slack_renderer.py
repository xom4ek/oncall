import json

import pytest

from apps.alerts.incident_appearance.renderers.slack_renderer import AlertGroupSlackRenderer
from apps.alerts.models import AlertGroup


@pytest.mark.django_db
def test_slack_renderer_acknowledge_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[0]
    assert button["text"]["text"] == "Acknowledge"
    assert json.loads(button["value"]) == {"organization_id": organization.pk, "alert_group_pk": alert_group.pk}


@pytest.mark.django_db
def test_slack_renderer_unacknowledge_button(
    make_organization, make_alert_receive_channel, make_alert_group, make_alert
):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel, acknowledged=True)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[0]
    assert button["text"]["text"] == "Unacknowledge"
    assert json.loads(button["value"]) == {"organization_id": organization.pk, "alert_group_pk": alert_group.pk}


@pytest.mark.django_db
def test_slack_renderer_resolve_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[1]
    assert button["text"]["text"] == "Resolve"
    assert json.loads(button["value"]) == {"organization_id": organization.pk, "alert_group_pk": alert_group.pk}


@pytest.mark.django_db
def test_slack_renderer_unresolve_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel, resolved=True)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[0]
    assert button["text"]["text"] == "Unresolve"
    assert json.loads(button["value"]) == {"organization_id": organization.pk, "alert_group_pk": alert_group.pk}


@pytest.mark.django_db
def test_slack_renderer_invite_action(
    make_organization, make_user, make_alert_receive_channel, make_alert_group, make_alert
):
    organization = make_organization()
    user = make_user(organization=organization)
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    ack_button = elements[2]
    assert ack_button["placeholder"]["text"] == "Invite..."

    # Check only user_id is passed. Otherwise, if there are a lot of users, the payload could be unnecessarily large.
    assert json.loads(ack_button["options"][0]["value"]) == {"user_id": user.pk}


@pytest.mark.django_db
def test_slack_renderer_stop_invite_button(
    make_organization, make_user, make_alert_receive_channel, make_alert_group, make_alert, make_invitation
):
    organization = make_organization()
    user = make_user(organization=organization)
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})
    invitation = make_invitation(alert_group, user, user)

    action = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[1]["actions"][0]

    assert action["text"] == f"Stop inviting {user.username}"
    assert json.loads(action["value"]) == {
        "organization_id": organization.pk,
        "alert_group_pk": alert_group.pk,
        "invitation_id": invitation.pk,
    }


@pytest.mark.django_db
def test_slack_renderer_silence_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[3]
    assert button["placeholder"]["text"] == "Silence"

    values = [json.loads(option["value"]) for option in button["options"]]
    assert values == [
        {"organization_id": organization.pk, "alert_group_pk": alert_group.pk, "delay": delay}
        for delay, _ in AlertGroup.SILENCE_DELAY_OPTIONS
    ]


@pytest.mark.django_db
def test_slack_renderer_unsilence_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel, silenced=True)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]
    button = elements[3]

    assert button["text"]["text"] == "Unsilence"
    assert json.loads(button["value"]) == {
        "organization_id": organization.pk,
        "alert_group_pk": alert_group.pk,
    }


@pytest.mark.django_db
def test_slack_renderer_attach_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel, silenced=True)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]
    button = elements[4]

    assert button["text"]["text"] == "Attach to ..."
    assert json.loads(button["value"]) == {
        "organization_id": organization.pk,
        "alert_group_pk": alert_group.pk,
    }


@pytest.mark.django_db
def test_slack_renderer_unattach_button(make_organization, make_alert_receive_channel, make_alert_group, make_alert):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)

    root_alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=root_alert_group, raw_request_data={})

    alert_group = make_alert_group(alert_receive_channel, root_alert_group=root_alert_group)
    make_alert(alert_group=alert_group, raw_request_data={})

    action = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["actions"][0]

    assert action["text"] == "Unattach"
    assert json.loads(action["value"]) == {
        "organization_id": organization.pk,
        "alert_group_pk": alert_group.pk,
    }


@pytest.mark.django_db
def test_slack_renderer_format_alert_button(
    make_organization, make_alert_receive_channel, make_alert_group, make_alert
):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[5]
    assert button["text"]["text"] == ":mag: Format Alert"
    assert json.loads(button["value"]) == {"organization_id": organization.pk, "alert_group_pk": alert_group.pk}


@pytest.mark.django_db
def test_slack_renderer_resolution_notes_button(
    make_organization, make_alert_receive_channel, make_alert_group, make_alert
):
    organization = make_organization()
    alert_receive_channel = make_alert_receive_channel(organization)
    alert_group = make_alert_group(alert_receive_channel)
    make_alert(alert_group=alert_group, raw_request_data={})

    elements = AlertGroupSlackRenderer(alert_group).render_alert_group_attachments()[0]["blocks"][0]["elements"]

    button = elements[6]
    assert button["text"]["text"] == "Add Resolution notes"
    assert json.loads(button["value"]) == {
        "organization_id": organization.pk,
        "alert_group_pk": alert_group.pk,
        "resolution_note_window_action": "edit",
    }
