FROM python:3
ARG GH_BRANCH=main
RUN --mount=type=cache,target=/root/.cache \
  pip install https://github.com/wtnb75/filterweb/archive/refs/heads/${GH_BRANCH}.zip
