---
layout: archive
title: "CV"
permalink: /cv/
description: "Curriculum vitae, publications, and background for Itai Shapira."
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

This page summarizes my background and research. For the full document, use the PDF version of my CV:

<p><a href="{{ base_path }}/files/resume.pdf" target="_blank" rel="noopener noreferrer"><strong>Download CV (PDF)</strong></a></p>

Research interests
======

Pluralistic AI alignment, algorithmic social choice, optimization, and multi-agent systems.

Current affiliation
======

PhD Candidate in Computer Science at Harvard University, advised by
<a href="https://procaccia.info/" target="_blank" rel="noopener noreferrer">Ariel D. Procaccia</a>.

Publications
======
<ul class="cv-publication-list">
  {% for publication in site.data.publications %}
    <li class="cv-publication-item">
      <div class="cv-publication-title-row">
        <span class="cv-publication-id">{{ publication.id }}</span>
        <strong>{{ publication.title }}</strong>
        <span class="cv-publication-year">{{ publication.year }}</span>
      </div>
      <div class="cv-publication-authors">{{ publication.authors_html }}</div>
      <div class="cv-publication-venue">{{ publication.venue }}{% if publication.note %} • {{ publication.note }}{% endif %}</div>
      <div class="cv-publication-links">
        {% for link in publication.links %}
          {% assign link_href = link.url %}
          {% unless link.url contains "://" %}
            {% assign link_href = base_path | append: link.url %}
          {% endunless %}
          <a href="{{ link_href }}" target="_blank" rel="noopener noreferrer">{{ link.label }}</a>{% unless forloop.last %} · {% endunless %}
        {% endfor %}
      </div>
    </li>
  {% endfor %}
</ul>

Selected online profiles
======

* <a href="https://scholar.google.com/citations?user=JOQXRbIAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>
* <a href="https://www.linkedin.com/in/itai-shapira-54583a2ab/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
* <a href="https://github.com/ishapira1" target="_blank" rel="noopener noreferrer">GitHub</a>
* <a href="https://x.com/IShapira1" target="_blank" rel="noopener noreferrer">X</a>
