FROM python:3.7.2-alpine3.7
EXPOSE 9990

ARG CURRENT_USER_ID=999
ARG CURRENT_GROUP_ID=999
ARG ENV
WORKDIR /app
RUN delgroup $(getent group ${CURRENT_GROUP_ID} | cut -d: -f1) || true && \
    addgroup -g ${CURRENT_GROUP_ID} -S hostuser && \
    adduser -D -s --system -u ${CURRENT_USER_ID} -G $(getent group ${CURRENT_GROUP_ID} | cut -d: -f1) hostuser

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

RUN apk add --no-cache --virtual .build-deps \
  libc-dev \
  gcc \
  libffi-dev

COPY --chown=hostuser:hostuser requirements.txt .
RUN pip3 install --default-timeout=100 -r requirements.txt

COPY --chown=hostuser:hostuser . .

USER hostuser

ENTRYPOINT ["python3", "main.py"]
