---
permalink: /
title: "Itai Shapira"
excerpt: "PhD researcher at Harvard working on pluralistic AI alignment, algorithmic social choice, and optimization."
author_profile: true
hide_title: true
redirect_from:
  - /about/
  - /about.html
---

<section class="home-hero">
  <h1 class="home-hero__name">{{ site.author.name }}</h1>
  <div class="about-bio">
    <p class="home-hero__lede">
      I'm a PhD Candidate in Computer Science at Harvard. I am privileged to be advised by
      <a href="https://procaccia.info/" target="_blank" rel="noopener noreferrer">Prof. Ariel D. Procaccia</a>.
    </p>
    <p>
      I study AI alignment: how human goals and values become training objectives, and how optimizing those objectives shapes AI behavior.
      I aim to understand the limitations of current alignment methods and develop better ones.
    </p>
    <p>
      In particular, I ask how AI can learn from our judgments (i) without inheriting their flaws, such as sycophancy;
      (ii) when those judgments conflict (pluralistic alignment); and
      (iii) when what we approve of differs from what ultimately serves us (multi-turn alignment).
    </p>
    <p>
      I am a <a href="https://www.siebelscholars.com/articles/siebel-scholars-foundation-announces-class-of-2027/" target="_blank" rel="noopener noreferrer">Siebel Scholar</a> (Class of 2027) and a recipient of the 2025 JPMorgan Chase PhD Fellowship. I am affiliated with the
      <a href="https://www.cmu.edu/ai-sdm/students/index.html" target="_blank" rel="noopener noreferrer">NSF AI Institute for Societal Decision Making</a>
      and serve on its Student Leadership Council.
    </p>
  </div>
</section>

<section class="home-section home-section--research home-section--selected-publications" aria-labelledby="selected-publications-heading">
  <div class="home-section-head">
    <div>
      <h2 id="selected-publications-heading">Selected Publications</h2>
    </div>
    <a class="home-view-all" href="{{ site.baseurl }}/research/">View all research <span aria-hidden="true">→</span></a>
  </div>
  {% include research.html featured_only=true compact=true minimal=true scrollable=false show_filters=false show_notation=true %}
</section>
