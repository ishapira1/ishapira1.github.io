# Itai Shapira's academic website

Source for [www.itai-shapira.com](https://www.itai-shapira.com), built with Jekyll and deployed through GitHub Pages.

## Main content

- `_pages/about.md`: homepage and biography
- `_data/publications.yml`: publication metadata used by Home, Research, and CV
- `_includes/projects.html`: selected projects and mentoring
- `_pages/cv.md`: HTML CV and link to the PDF CV
- `_pages/privacy.md`: site privacy notice

## Local preview

```sh
bundle install
bundle exec jekyll serve --config _config.yml,_config.local-preview.yml
```

The local-preview configuration disables Google Analytics so development traffic does not enter production reports.
