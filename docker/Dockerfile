FROM python:3
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,target=tmp \
  pip install tmp/*.whl
