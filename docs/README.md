tisane docs
===========

## Directory structure

- `_templates`: the templates to use to generate documentation, adapted from numpy's
- `reference`: contains rst files for the API reference documentation, which are used to generate the structure
- `src/html`: the html files that are served
  - `src/html/_static/css`: style sheets
  - `src/html/_static/js`: javascript

## How to make

In this directory, run `make`. There will be a ton of errors that come up, but this is expected.

To update the documentation on the site, just add the updated files with `git add -u`. (Note that if you added any new files, you will need to add them yourself with `git add <my-new-html-file>`.)
