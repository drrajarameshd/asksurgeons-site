---
title: "Our Doctors"
layout: page
permalink: /doctors/
description: "Meet the AskSurgeons doctors — specialist profiles, bios, and quick booking links to app.asksurgeons.com."
robots: index,follow
---

{% comment %}
Constants / Config — edit here if things change
{% endcomment %}
{% assign DOCTOR_IMG_PATH = "/assets/images/doctors/" %}
{% assign BOOKING_BASE_URL = "https://app.asksurgeons.com/?doctor=" %}
{% assign DEFAULT_IMG = "/assets/images/doctors/default.webp" %}

<section class="page-header">
  <h1>{{ page.title }}</h1>
  <p>Our network of experienced surgeons and physicians. Read their bios, then book a consultation at 
     <a href="https://app.asksurgeons.com" target="_blank" rel="noopener">app.asksurgeons.com</a>.
  </p>
</section>

<div class="doctor-grid" style="display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:1.25rem; align-items:start;">
  {%- for doc in site.data.doctors -%}
    {%- assign name = doc.name | default: "Unknown" -%}
    {%- assign slug = name | slugify -%}
    {%- assign image_path = doc.image | default: "" -%}

    {%- if image_path == "" -%}
      {%- assign final_img = DEFAULT_IMG -%}
    {%- else -%}
      {%- assign final_img = DOCTOR_IMG_PATH | append: image_path -%}
    {%- endif -%}

    <article class="doctor-card" style="border:1px solid #e6eef6; padding:1rem; border-radius:8px; background:#fff;">
      <a href="/doctors/{{ slug }}/" style="text-decoration:none; color:inherit;">
        <div style="display:flex; gap:0.75rem; align-items:center;">
          <img src="{{ final_img }}" alt="{{ name }}" width="84" height="84" style="object-fit:cover; width:84px; height:84px; border-radius:8px;" loading="lazy">
          <div style="flex:1; min-width:0;">
            <h3 style="margin:0 0 0.25rem 0; font-size:1.05rem;">{{ name }}</h3>
            {% if doc.speciality %}
              <div style="font-size:0.92rem; color:#445566;">{{ doc.speciality }}</div>
            {% endif %}
            {% if doc.department %}
              <div style="font-size:0.82rem; color:#6b7c8e; margin-top:0.35rem;">{{ doc.department }}</div>
            {% endif %}
          </div>
        </div>
      </a>

      <div style="margin-top:0.6rem; display:flex; gap:0.5rem; align-items:center;">
        <a class="btn" href="{{ BOOKING_BASE_URL | append: name | url_encode }}" target="_blank" rel="noopener" 
           style="padding:0.45rem 0.65rem; border-radius:6px; border:1px solid var(--theme-color); background:var(--theme-color); color:#fff; text-decoration:none;">
          Book
        </a>

        <a href="/doctors/{{ slug }}/" style="padding:0.45rem 0.65rem; border-radius:6px; border:1px solid #d3e6f8; background:#f8fbff; color:var(--theme-color); text-decoration:none;">
          Profile
        </a>
      </div>
    </article>
  {%- endfor -%}
</div>
