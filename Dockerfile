FROM python:3.9.6-slim-buster AS base-image

MAINTAINER Jonathan Sick <jsick@lsst.org>

ENV APPDIR /ltd-dasher
COPY . $APPDIR/
WORKDIR $APPDIR
RUN pip install -r requirements.txt

RUN groupadd -r uwsgi_grp && useradd -r -g uwsgi_grp uwsgi

RUN chown -R uwsgi:uwsgi_grp $APPDIR

USER uwsgi

EXPOSE 3031

CMD ["uwsgi", "uwsgi.ini"]
