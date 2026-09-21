# Family Portal

A cheerful, mobile-friendly family schedule and to-do page for Kaiya, Mom, and Dad.

## Features

- Separate kid and grown-up views
- Daily check-in for feelings and the day of the week
- Visual morning, afternoon, and evening task cards
- One-time and repeating schedule items
- Add, edit, and remove tasks from the grown-up view
- Device-local progress, preferences, and PIN storage
- Light and dark themes
- Text-to-speech labels

## Run locally

This is a static site with no build step. Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 4173
```

Then visit <http://localhost:4173>.

The initial grown-up PIN is `123`. It can be changed in Grown-up settings.

## Deploy

The repository can be published directly with GitHub Pages using the root of the `main` branch.
