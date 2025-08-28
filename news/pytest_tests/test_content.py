from django.conf import settings
from django.urls import reverse
import pytest
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
def test_news_count_and_order(client, news_column):
    object_list = client.get(reverse('news:home')).context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    all_timestamps = [
        comment.created for comment in response.context[
            'news'].comment_set.all()]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, need_form_in_context',
                         [(lf('client'), False),
                          (lf('author_client'), True),],)
def test_comment_form_availability_for_users(parametrized_client,
                                             need_form_in_context,
                                             news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(detail_url)
    if need_form_in_context:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context
