# syntax=docker/dockerfile:1

# Pin to a minor version; for fully reproducible builds pin by digest too
# (docker buildx imagetools inspect <image>) and let Dependabot bump it.
ARG RUBY_VERSION=3.4
ARG NGINX_VERSION=1.28

# ---------- Stage 1: build the Jekyll site ----------
FROM ruby:${RUBY_VERSION}-slim-bookworm AS build

# Native gems (and some themes) need a compiler and git
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /site

# Copy only the dependency files first so this layer is cached
# until the Gemfile changes. Use the same Bundler version that
# wrote the lockfile.
COPY Gemfile Gemfile.lock* ./
RUN gem install bundler -v "$(tail -n 1 Gemfile.lock | tr -d ' ')" --no-document \
 && bundle install --jobs 4 --retry 3

COPY . .

# "COPY . ." brought back the original Gemfile.lock (which lists the Windows
# platform), so the platform has to be removed AFTER that copy. This only
# changes the lockfile inside the image, not the one in your repo.
RUN bundle lock --remove-platform x64-mingw-ucrt || true

ENV JEKYLL_ENV=production
# --baseurl "" because the container serves the site at the root,
# not under /austin_kz_directory like GitHub Pages does
RUN bundle exec jekyll build --baseurl "" --destination /out

# ---------- Stage 2: serve with nginx (non-root) ----------
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION}-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /out /usr/share/nginx/html

# nginx-unprivileged already runs as the non-root user "nginx" (uid 101)
# and listens on 8080, so no root privileges are needed.
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
