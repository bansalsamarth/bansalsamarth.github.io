---
layout: page
title: Blog Archive
<!-- published: true -->
---

{% for post in site.posts %}
<!--
{{ post.date | date_to_string }} &raquo; [ {{ post.title }} ]({{ post.url }})   -->




**[ {{ post.title }} ]({{post.url}})**  <br> *{{ post.date | date_to_string }}* <br>

{{post.desc}}

---

<!-- [ {{ post.title }} ]({{ post.url }})  &raquo;  -->




{% endfor %}


<!-- ##Technology

* [Facebook and free spech, explained](2018/07/28/facebook-free-seech/)
* Interesting readings on quantum crpytography

##Indian Politics


##Indian Economy
* Demonetisation
* GST
* Agriculture

##International Politics
* Pakistan Election

##Politics

* Universal Basic Income
* Primary healthcare in India
* Air Pollution -->
