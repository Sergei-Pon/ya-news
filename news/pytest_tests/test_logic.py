from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from pytest_lazy_fixtures import lf

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, comments_count',
                         [(lf('client'), 0),
                          (lf('author_client'), 1),],)
def test_create_comment_availability_for_users(parametrized_client,
                                               comments_count,
                                               comment_form_data,
                                               pk_for_args):
    parametrized_client.post(reverse('news:detail', args=pk_for_args),
                             data=comment_form_data)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(author_client, pk_for_args):
    assertFormError(
        form=author_client.post(
            reverse('news:detail', args=pk_for_args),
            data={'text': f'{BAD_WORDS[0]}'}).context['form'],
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client,
                                 comment_form_data,
                                 comment_pk_for_args,
                                 pk_for_args, comment):
    assertRedirects(author_client.post(
        reverse('news:edit', args=comment_pk_for_args), comment_form_data
    ), reverse('news:detail', args=pk_for_args) + '#comments')
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


def test_other_user_cant_edit_comment(not_author_client,
                                      comment_form_data,
                                      comment_pk_for_args):
    assert not_author_client.post(
        reverse('news:edit', args=comment_pk_for_args),
        comment_form_data).status_code == HTTPStatus.NOT_FOUND


def test_author_can_delete_comment(author_client,
                                   comment_pk_for_args,
                                   pk_for_args):
    assertRedirects(author_client.post(
        reverse('news:delete', args=comment_pk_for_args)
    ), reverse('news:detail', args=pk_for_args) + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client,
                                     comment_pk_for_args):
    assert not_author_client.post(
        reverse('news:delete', args=comment_pk_for_args)
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
