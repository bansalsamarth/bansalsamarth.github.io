---
layout: page
title: Blog
<!-- published: true -->
---

<em>I now blog at https://listed.to/@bansalsamarth </em>

{% for post in site.posts %}
<!--
{{ post.date | date_to_string }} &raquo; [ {{ post.title }} ]({{ post.url }})   -->




 *{{ post.date | date_to_string }}* **[ {{ post.title }} ]({{post.url}})** <br>

{{post.desc}}

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
