from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize('name, args',
                         [('news:home', None),
                          ('news:detail', lf('pk_for_args')),
                          ('users:login', None),
                          ('users:logout', None),
                          ('users:signup', None),],)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    assert (client.get(url) if name != 'users:logout' else client.post(url)
            ).status_code == HTTPStatus.OK


@pytest.mark.parametrize('parametrized_client, expected_status',
                         [(lf('not_author_client'), HTTPStatus.NOT_FOUND),
                          (lf('author_client'), HTTPStatus.OK),],)
@pytest.mark.parametrize('name',
                         ('news:edit', 'news:delete'),)
def test_pages_availability_for_different_users(parametrized_client,
                                                name,
                                                comment,
                                                expected_status):
    assert (parametrized_client.get(reverse(name, args=(comment.pk,)))
            ).status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name, args',
                         [('news:edit', lf('pk_for_args')),
                          ('news:delete', lf('pk_for_args')),],)
def test_redirects_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    assertRedirects(client.get(url), f'{reverse('users:login')}?next={url}')
