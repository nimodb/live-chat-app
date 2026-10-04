# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Real-time chat app built on Django 6.1, Django Channels (Daphne) and WebSockets, with an HTMX + Tailwind front end rendered from Django templates. Auth is django-allauth.

## Commands

Use Python 3.12 or newer (Django 6.1 needs 3.12+). The virtualenv lives in `.venv` (currently Python 3.14).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python manage.py migrate
.venv/bin/python manage.py initialize_chat_groups   # required once per database, see below
.venv/bin/python manage.py runserver                # Daphne ASGI server, http://127.0.0.1:8000

.venv/bin/python manage.py test                     # all tests
.venv/bin/python manage.py test rtchat.tests.SomeTestCase.test_method   # single test
```

CSS is built with the Tailwind CLI (v3, Node required only for this step). The source is `assets/tailwind.css`, which holds the `@tailwind` directives plus all custom classes (`green-dot`, `hoverlist`, buttons, form defaults, ...); the output `static/css/style.css` is committed. Tailwind only emits utilities it finds in the files listed in `tailwind.config.js` (templates and `forms.py`), so rebuild after adding or changing classes:

```bash
npm install
npm run build:css      # or: npm run watch:css
```

The `tests.py` files are still empty stubs. No linter or formatter is configured.

## Settings

`core/settings/` is split into `common.py`, `dev.py` and `prod.py`. `manage.py`, `core/asgi.py` and `core/wsgi.py` all default `DJANGO_SETTINGS_MODULE` to `core.settings.dev`; production must set it to `core.settings.prod` explicitly.

Static files: sources live in `static/` (tracked, listed in `STATICFILES_DIRS`); `collectstatic` writes to `staticfiles/` (`STATIC_ROOT`, gitignored). WhiteNoise serves `/static/` in both modes; `prod.py` uses `CompressedManifestStaticFilesStorage`, so run `collectstatic` before starting with `DEBUG=False` and reference files only through `{% static %}` (a missing file is a 500 there). `static/unpkg/` holds vendored Alpine 3.17.4 (`cdn.min.js`), htmx 2.0.11 (`htmx.js`) and the htmx WebSocket extension htmx-ext-ws 2.0.4 (`ws.js`). Icons are in `static/images/icons/`. hyperscript 0.9.12 is vendored there too (`_hyperscript.min.js`). Uploaded media is only served when `DEBUG` is on.

- `dev.py`: SQLite, in-memory channel layer (no Redis needed), console email backend, debug toolbar.
- `prod.py`: Redis channel layer, `SECRET_KEY` from the environment. `ALLOWED_HOSTS` and the Redis host are `xxxxxxx` placeholders, and no `DATABASES` is defined.

The in-memory channel layer only works within a single process, so in dev messages don't cross between server processes.

## Things that break on a fresh clone

- **Default chat groups.** `chat_view` defaults to the `public-chat` group and `OnlineStatusConsumer` (connected from the footer of every page) looks up `online-status`. Both 404 until `initialize_chat_groups` has been run.
- **Email verification gate.** Most chat views use `@verified_required` (`rtchat/decorators.py`), which redirects users without a verified allauth `EmailAddress` to `profile-settings`. In dev the confirmation link is printed to the server console. Since Django 6 the console backend prints the body quoted-printable, so the link is wrapped with a trailing `=` that has to be removed when copying it.

## Architecture

### Apps

- `core` — settings, root URLconf, ASGI entrypoint.
- `rtchat` — chat models, HTTP views, WebSocket consumers. Mounted at `/`, so the site home page is the public chat.
- `users` — `Profile` model, profile/settings views, user signals.
- `home` — unused leftover.

### Chat model

One `ChatGroup` model covers three kinds of room, distinguished by fields rather than subclasses:

- public chat: the row with `group_name="public-chat"`
- private 1:1 chat: `is_private=True`, exactly two `members`
- named group chat: `groupchat_name` set, has an `admin`, users join by visiting the URL

`group_name` is the unique room key used in URLs and as the Channels group name; it is auto-filled with a shortuuid in `save()` when blank. `online-status` is also a `ChatGroup` row, used purely to track site-wide presence through its `users_online` M2M.

### Real-time flow

`core/asgi.py` routes HTTP to Django and WebSockets through `AuthMiddlewareStack` to `rtchat/routing.py`. Both consumers are synchronous `WebsocketConsumer`s that call the channel layer through `async_to_sync` and use the ORM directly.

The server never sends JSON to the browser. Consumers render template partials with `render_to_string` and send the HTML; each partial carries `hx-swap-oob` so the HTMX `ws` extension swaps it into the right element by id. Changing an element id in a partial means changing the matching id in the page template. A partial must only send elements whose id exists on the receiving page: htmx (2.0.5+) logs an `htmx:oobErrorNoTarget` console error otherwise, which is why `online_count.html` branches on the room type and skips the viewer's own dot.

- **Text message:** the form in `chat.html` uses `ws-send` → `ChatRoomConsumer.receive` creates the `GroupMessage` → `group_send` with type `message_handler` → each connected consumer renders `partials/chat_message_p.html` for its own user (so "mine vs theirs" styling is per recipient).
- **File message:** uploaded over plain HTTP (`chat_file_upload`, `hx-post`), then the view pushes the same `message_handler` event into the channel layer via `get_channel_layer()`.
- **Presence:** `ChatRoomConsumer` adds/removes the user from the room's `users_online` on connect/disconnect and broadcasts `online_count.html`. `OnlineStatusConsumer` does the same for the site-wide group and broadcasts `online_status.html`.

### Users

`users/signals.py` creates a `Profile` whenever a `User` is created, lowercases usernames on save, and keeps the allauth `EmailAddress` in sync with `User.email` (resetting `verified` when it changes). `LOGIN_REDIRECT_URL` is `/`.

### URLs worth knowing

- `/admin/` is a honeypot (`admin_honeypot`); the real Django admin is at `/91v9/`.
- `/@<username>/` is the public profile page.
