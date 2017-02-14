"""Template rendering functions."""

import os
import datetime
import re

from structlog import get_logger
import jinja2

from .jinjafilters import filter_simple_date


# regular expression that matches tickets/DM-N ticket branches
TICKET_BRANCH_PATTERN = re.compile('^tickets/([A-Z]+-[0-9]+)')


def render_edition_dashboard(product_data, edition_data,
                             asset_dir='/_dasher-assets'):
    """Render the edition template with data."""
    logger = get_logger()
    logger.debug('render_edition_dashboard')

    env = create_jinja_env()

    # hydrate the datasets with datetime objects
    _insert_datetime(edition_data)
    _insert_age(edition_data)

    _insert_github_ref_url(product_data, edition_data)
    _insert_jira_url(edition_data)

    # The main edition is always a release; label it as 'Current' for
    # template presentation.
    # More work should be done on how LTD designates releases.
    if 'main' in edition_data:
        releases = [edition_data['main']]
        releases[0]['alt_title'] = 'Current'
    else:
        releases = []
    release_slugs = [r['slug'] for r in releases]

    # Extract recently-updated editions
    # Releases are never included in the development lists
    recent_threshold = datetime.timedelta(days=7)
    recents = []
    stales = []
    for _, edition in edition_data.items():
        if edition['slug'] not in release_slugs:
            if edition['age'] <= recent_threshold:
                recents.append(edition)
            else:
                stales.append(edition)

    # Sort editions youngest to oldest
    releases.sort(key=lambda x: x['age'])
    recents.sort(key=lambda x: x['age'])
    stales.sort(key=lambda x: x['age'])

    template = env.get_template('edition_dashboard.jinja')
    rendered_page = template.render(
        asset_dir=asset_dir,
        product=product_data,
        releases=releases,
        recents=recents,
        stales=stales)
    return rendered_page


def render_build_dashboard(product_data, build_data,
                           asset_dir='/_dasher-assets'):
    """Render the builds template with data."""
    logger = get_logger()
    logger.debug('render_build_dashboard')

    env = create_jinja_env()

    # hydrate the datasets with datetime objects
    _insert_datetime(build_data, datetime_str_key='date_created')
    _insert_age(build_data, datetime_str_key='date_created')

    builds = [b for _, b in build_data.items()]
    builds.sort(key=lambda x: x['age'])
    template = env.get_template('build_dashboard.jinja')
    rendered_page = template.render(
        asset_dir=asset_dir,
        product=product_data,
        builds=builds)
    return rendered_page


def create_jinja_env():
    """Create a Jinja2 `~jinja2.Environment`.

    Returns
    -------
    env : `jinja2.Environment`
        Jinja2 template rendering environment, configured to use templates in
        ``templates/``.
    """
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html'])
    )
    env.filters['simple_date'] = filter_simple_date
    return env


def _insert_datetime(dataset,
                     datetime_str_key='date_rebuilt',
                     datetime_key='datetime_rebuilt'):
    """Inserts a field into every item of an editions
    or build dataset with a `datetime.datetime` instance corresponding to a
    ISO datetime string from the Keeper API.
    """
    for k, d in dataset.items():
        d[datetime_key] = _parse_keeper_datetime(d[datetime_str_key])
    return dataset


def _insert_age(dataset,
                datetime_str_key='date_rebuilt',
                age_key='age'):
    """Inserts the age (from now) of a build into every item of an edition
    or build dataset.

    Age is persisted as a `datetime.timedelta` instance.
    """
    for k, d in dataset.items():
        dt = _parse_keeper_datetime(d[datetime_str_key])
        d[age_key] = datetime.datetime.now() - dt
    return dataset


def _insert_github_ref_url(product, edition_dataset, key='github_ref_url'):
    """Insert the GitHub branch URL for every edition.

    FIXME: this is an MVP for single-repo products. This needs to be
    re-thought for multi-repo LTD products.
    """
    base_repo_url = product['doc_repo'].rstrip('.git')
    for k, d in edition_dataset.items():
        git_ref = d['tracked_refs'][0]
        # https://github.com/lsst-sqre/ltd-dasher/tree/tickets/DM-9023
        url = base_repo_url + '/tree/' + git_ref
        d[key] = url


def _insert_jira_url(edition_dataset,
                     url_key='jira_url', name_key='jira_ticket_name'):
    """Insert the name and URL of a JIRA ticket associated with an edition.

    FIXME: this is an MVP for single-repo products. This needs to be
    re-thought for multi-repo LTD products.
    """
    for k, d in edition_dataset.items():
        git_ref = d['tracked_refs'][0]
        match = TICKET_BRANCH_PATTERN.search(git_ref)
        if match is not None:
            ticket_name = match.group(1)
            d[name_key] = ticket_name
            d[url_key] = 'https://jira.lsstcorp.org/browse/{0}'.format(
                ticket_name)


def _parse_keeper_datetime(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')


def render_development_index():
    """Render an index.html document for the root of the development builds.
    """
    env = create_jinja_env()
    template = env.get_template('dev_index.jinja')
    rendered_page = template.render()
    return rendered_page


def write_html(page_data, path):
    """Write a rendered HTML template to the file system (for development)."""
    dirname = os.path.dirname(path)
    if dirname is not '' and not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(page_data)
