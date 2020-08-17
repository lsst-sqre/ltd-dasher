"""Template rendering functions."""

import os
import datetime
import re

from structlog import get_logger
import jinja2

from .jinjafilters import filter_simple_date


# regular expression that matches tickets/DM-N ticket branches
TICKET_BRANCH_PATTERN = re.compile(r'^tickets/([A-Z]+-[0-9]+)')

# regular expression that matches a document handle as a slug
DOC_HANDLE_PATTERN = re.compile(r'^(sqr|dmtn|smtn|ldm|lse|lpm|dmtr)-[0-9]+$')

# regular expression that matches version strings
RELEASE_PATTERN = re.compile(r'^v\d+')

# map of series handles to descriptive names
SERIES_NAMES = {
    'sqr': 'SQuaRE Technical Note',
    'dmtn': 'Data Management Technical Note',
    'smtn': 'Simulations Technical Note',
    'ldm': 'LSST Data Management',
    'lse': 'LSST Systems Engineering',
    'lpm': 'LSST Project Management',
    'dmtr': 'Data Management Test Report',
}


def render_edition_dashboard(product_data, edition_data,
                             asset_dir='/_dasher-assets'):
    """Render the edition template with data."""
    logger = get_logger()
    logger.debug('render_edition_dashboard')

    env = create_jinja_env()

    # hydrate the datasets with datetime objects
    _insert_datetime(edition_data)
    _insert_age(edition_data)

    _insert_github_handle(product_data)
    _insert_ci_data(product_data)
    _insert_github_ref_url(product_data, edition_data)
    _insert_jira_url(edition_data)
    _insert_doc_handle(product_data)
    _insert_is_release(edition_data)
    _normalize_product_title(product_data)

    # The main edition is always a release; label it as 'Current' for
    # template presentation.
    # More work should be done on how LTD designates releases.
    if 'main' in edition_data:
        edition_data['main']['alt_title'] = 'Current'
        edition_data['main']['is_release'] = True

    # Extract recently-updated editions
    # Releases are never included in the development lists
    development_editions = []
    release_editions = []
    for _, edition in edition_data.items():
        if edition['is_release']:
            release_editions.append(edition)
        else:
            development_editions.append(edition)

    # Sort editions youngest to oldest
    release_editions.sort(key=lambda x: x['age'])
    development_editions.sort(key=lambda x: x['age'])

    template = env.get_template('edition_dashboard.jinja')
    rendered_page = template.render(
        asset_dir=asset_dir,
        product=product_data,
        releases=release_editions,
        development_editions=development_editions)
    return rendered_page


def render_build_dashboard(product_data, build_data,
                           asset_dir='/_dasher-assets'):
    """Render the builds template with data."""
    logger = get_logger()
    logger.debug('render_build_dashboard')

    env = create_jinja_env()

    # hydrate the datasets with datetime objects
    _insert_datetime(build_data,
                     datetime_str_key='date_created',
                     datetime_key='datetime_created')
    _insert_age(build_data,
                datetime_str_key='date_created')

    _insert_ci_data(product_data)
    _insert_doc_handle(product_data)
    _insert_github_ref_url(product_data, build_data,
                           git_refs_key='git_refs')
    _insert_jira_url(build_data,
                     git_refs_key='git_refs')
    _normalize_product_title(product_data)

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


def _insert_github_ref_url(product, edition_dataset,
                           git_refs_key='tracked_refs',
                           key='github_ref_url'):
    """Insert the GitHub branch URL for every edition.

    FIXME: this is an MVP for single-repo products. This needs to be
    re-thought for multi-repo LTD products.
    """
    base_repo_url = product['doc_repo'].rstrip('.git')
    for k, d in edition_dataset.items():
        # Editions that don't use the git_refs tracking mode will have
        # tracked_refs equal to None.
        try:
            git_ref = d[git_refs_key][0]
        except TypeError:
            # None is not indexable
            continue

        # https://github.com/lsst-sqre/ltd-dasher/tree/tickets/DM-9023
        url = base_repo_url + '/tree/' + git_ref
        d[key] = url


def _insert_jira_url(edition_dataset, git_refs_key='tracked_refs',
                     url_key='jira_url', name_key='jira_ticket_name'):
    """Insert the name and URL of a JIRA ticket associated with an edition.

    FIXME: this is an MVP for single-repo products. This needs to be
    re-thought for multi-repo LTD products.
    """
    for k, d in edition_dataset.items():
        # Editions that don't use the git_refs tracking mode will have
        # tracked_refs equal to None.
        try:
            git_ref = d[git_refs_key][0]
        except TypeError:
            # None is not indexable
            continue

        match = TICKET_BRANCH_PATTERN.search(git_ref)
        if match is not None:
            ticket_name = match.group(1)
            d[name_key] = ticket_name
            d[url_key] = 'https://jira.lsstcorp.org/browse/{0}'.format(
                ticket_name)


def _insert_github_handle(product, handle_key='github_handle'):
    """Insert a friendly GitHub handle, like ``lsst/pipelines_lsst_io``, into
    the product dataset.
    """
    repo_url = product['doc_repo']
    repo_handle = repo_url.rstrip('.git')
    repo_handle = repo_handle.lstrip('https://github.com/')
    product[handle_key] = repo_handle


def _insert_ci_data(product,
                    url_key='ci_url',
                    name_key='ci_platform_name'):
    """Insert the name and URL of the CI dashboard.

    FIXME this is a hack; we can't assume that a product is being built
    with Travis. Instead, this metadata needs to be given by Keeper or
    DocHub.
    """
    repo_url = product['doc_repo']
    repo_handle = repo_url.rstrip('.git')
    repo_handle = repo_handle.lstrip('https://github.com/')
    ci_url = 'https://travis-ci.org/{0}'.format(repo_handle)
    ci_name = 'Travis'
    product[url_key] = ci_url
    product[name_key] = ci_name


def _insert_doc_handle(product, handle_key='doc_handle',
                       series_name_key='series_name'):
    """Insert the document handle, if available.

    Also process the title so that the document handle is not repeated in the
    title.
    """
    match = DOC_HANDLE_PATTERN.search(product['slug'])
    if match is not None:
        # set handle_key field only if there's a document handle;
        # this behaviour is used by the template
        product[handle_key] = product['slug'].upper()
        product[series_name_key] = SERIES_NAMES[match.group(1).lower()]


def _normalize_product_title(product):
    """Remove the handle prefix from a product title, if present."""
    if 'doc_handle' in product:
        if product['title'].startswith(product['doc_handle']):
            product['title'] = product['title'][len(product['doc_handle']):]
    product['title'] = product['title'].strip(': ')


def _insert_is_release(editions,
                       is_release_key='is_release',
                       alt_title_key='alt_title'):
    """Insert a field indicating whether this edition is likely a release or
    not.

    Heuristic for guessing a release: edition slug begins with `v` and a digit.
    """
    for k, d in editions.items():
        slug = d['slug']
        match = RELEASE_PATTERN.search(slug)
        if match is not None:
            d[is_release_key] = True
            d[alt_title_key] = slug
        else:
            d[is_release_key] = False


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
