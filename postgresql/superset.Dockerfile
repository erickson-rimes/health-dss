# Use the official Superset image as the base
FROM apache/superset:latest

RUN pip install Flask-OpenID
RUN pip install Flask-OIDC==2.2.0

