class Header extends HTMLElement {
  constructor() {
    super();
  }

connectedCallback() {
  this.innerHTML = `
  <header>
    <nav>
          <a class="site-title" href="index.html">samarthbansal.com</a>
          <ul>
              <li><a class="nav" href="media.html">Now</a></li>
              <li><a class="nav" href="articles.html">Published Work</a></li>
              <li>Public Journal
                  <ul>
                    <li><a class="nav" href="links.html">Media Matters</a></li>
                    <li><a class="nav" href="tools.html">Fitness</a></li>
                    <li><a class="nav" href="templates.html">Reading</a></li>
                  </ul>
              </li>
              <li><a class="nav" href="articles.html">Blog</a></li>
              <li><a class="nav" href="articles.html">Contact</a></li>
          </ul>

      </nav>
   </header>
    `;
  }
}

customElements.define('header-component', Header);
