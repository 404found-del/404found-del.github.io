source "https://rubygems.org"

gem "jekyll", "~> 4.3"

# Required by kramdown.input: GFM in _config.yml. It arrives as a Jekyll
# transitive dependency, but the config depends on it directly, so declare it.
gem "kramdown-parser-gfm", "~> 1.1"

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end

# Windows needs timezone data bundled
gem "tzinfo-data", platforms: [:windows]
